from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ultralytics import YOLO
from PIL import Image
import io
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from .models import FoodItem, PortionType
from .serializers import FoodNutritionRequestSerializer


# Load model ONCE 
MODEL_PATH = "models/best.pt"
model = YOLO(MODEL_PATH)


class FoodRecognitionAPIView(APIView):
    """
    POST image -> returns predicted food name, confidence, portion_type
    """
    permission_classes = [AllowAny]

    def post(self, request):
        image_file = request.FILES.get("image")

        if not image_file:
            return Response(
                {"error": "Image is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Read image
            image_bytes = image_file.read()
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

            # Run classification
            results = model.predict(image, verbose=False)
            probs = results[0].probs

            top_index = probs.top1
            confidence = float(probs.top1conf)

            # Normalize label for DB lookup
            label = str(model.names[top_index]).strip().lower()

            # Find food in DB
            food_obj = FoodItem.objects.filter(name=label, is_active=True).first()

            portion_type = food_obj.portion_type if food_obj else None

            print(
                f"[FoodRecognition] Detected: {label} | "
                f"Confidence: {confidence:.4f} | "
                f"PortionType: {portion_type}"
            )

            return Response({
                "food": label,
                "confidence": round(confidence, 4),
                "portion_type": portion_type,  # 👈 important
            })

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class FoodNutritionAPIView(APIView):
    """
    POST:
      - { "food": "momo", "pieces": 10 }
      - { "food": "dalbhat", "size": "medium" }

    Returns macros totals.
    """
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = FoodNutritionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        food_name = serializer.validated_data["food"]
        pieces = serializer.validated_data.get("pieces")
        size = serializer.validated_data.get("size")

        # Find food + nutrition
        food = get_object_or_404(FoodItem, name=food_name, is_active=True)

        # Ensure nutrition exists
        nutrition = getattr(food, "nutrition", None)
        if not nutrition:
            return Response(
                {"error": f"Nutrition data not found for '{food.name}'"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # COUNTABLE -> needs pieces
        if food.portion_type == PortionType.COUNTABLE:
            if pieces is None:
                return Response(
                    {"error": "This food is countable. Please provide 'pieces'."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Ensure per_piece values exist
            if nutrition.calories_per_piece is None:
                return Response(
                    {"error": f"Per-piece nutrition not set for '{food.name}'"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            calories = (nutrition.calories_per_piece or 0) * pieces
            protein = (nutrition.protein_per_piece or 0) * pieces
            carbs = (nutrition.carbs_per_piece or 0) * pieces
            fat = (nutrition.fat_per_piece or 0) * pieces

            return Response({
                "food": food.name,
                "portion_type": food.portion_type,
                "unit": "piece",
                "quantity": pieces,
                "calories": round(calories, 2),
                "protein": round(protein, 2),
                "carbs": round(carbs, 2),
                "fat": round(fat, 2),
            })

        # PORTION -> needs size
        if food.portion_type == PortionType.PORTION:
            if not size:
                return Response(
                    {"error": "This food uses portion sizes. Please provide 'size' (small/medium/large)."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            cal = getattr(nutrition, f"calories_{size}", None)
            pro = getattr(nutrition, f"protein_{size}", None)
            car = getattr(nutrition, f"carbs_{size}", None)
            fat = getattr(nutrition, f"fat_{size}", None)

            if cal is None:
                return Response(
                    {"error": f"Portion nutrition not set for '{food.name}' size '{size}'"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response({
                "food": food.name,
                "portion_type": food.portion_type,
                "unit": "portion",
                "size": size,
                "calories": round(float(cal or 0), 2),
                "protein": round(float(pro or 0), 2),
                "carbs": round(float(car or 0), 2),
                "fat": round(float(fat or 0), 2),
            })

        return Response({"error": "Invalid portion type on food item"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
