from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ultralytics import YOLO
from PIL import Image
import io
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from .models import FoodItem, PortionType,FoodLog
from .serializers import FoodNutritionRequestSerializer,FoodLogCreateSerializer,FoodLogSerializer
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from utils.calculate_nutr import compute_nutrition
from rest_framework.permissions import IsAuthenticated
from django.utils.dateparse import parse_date
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.utils import timezone
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
            # Save image
            image_path = default_storage.save(
                f"food_detection/{image_file.name}",
                ContentFile(image_file.read())
            )
            image_url = request.build_absolute_uri(default_storage.url(image_path))

            # Re-open image for model
            image = Image.open(default_storage.open(image_path)).convert("RGB")

            # Run classification
            results = model.predict(image, verbose=False)
            probs = results[0].probs

            top_index = probs.top1
            confidence = float(probs.top1conf)
            label = str(model.names[top_index]).strip().lower()

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
                "portion_type": portion_type,
                "image_url": image_url,
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
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = FoodNutritionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        food_name = serializer.validated_data["food"]
        pieces = serializer.validated_data.get("pieces")
        size = serializer.validated_data.get("size")

        food = get_object_or_404(FoodItem, name=food_name, is_active=True)

        nutrition = getattr(food, "nutrition", None)
        if not nutrition:
            return Response(
                {"error": f"Nutrition data not found for '{food.name}'"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            result = compute_nutrition(food, pieces=pieces, size=size)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "food": food.name,
            "portion_type": food.portion_type,
            **{k: round(v, 2) if isinstance(v, (int, float)) else v for k, v in result.items()}
        })


class EatFoodAPIView(APIView):
    """
    Saves FoodLog only when user presses EAT
    """
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = FoodLogCreateSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        log = serializer.save()

        return Response(
            FoodLogCreateSerializer(log).data,
            status=status.HTTP_201_CREATED
        )
    

class FoodLogListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FoodLogSerializer

    def get_queryset(self):
        qs = FoodLog.objects.filter(
            user=self.request.user
        ).select_related("food_item")

        params = self.request.query_params

        # ✅ TODAY filter
        if params.get("today") == "true":
            today = timezone.localdate()
            return qs.filter(created_at__date=today).order_by("-created_at")

        # Existing filters
        date_str = params.get("date")
        start_str = params.get("start_date")
        end_str = params.get("end_date")

        if date_str:
            d = parse_date(date_str)
            if not d:
                raise ValidationError({"date": "Use YYYY-MM-DD"})
            qs = qs.filter(created_at__date=d)

        if start_str:
            sd = parse_date(start_str)
            if not sd:
                raise ValidationError({"start_date": "Use YYYY-MM-DD"})
            qs = qs.filter(created_at__date__gte=sd)

        if end_str:
            ed = parse_date(end_str)
            if not ed:
                raise ValidationError({"end_date": "Use YYYY-MM-DD"})
            qs = qs.filter(created_at__date__lte=ed)

        return qs.order_by("-created_at")

class DailySummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.localdate()
        
        # Sum of calories eaten today
        logs = FoodLog.objects.filter(user=user, created_at__date=today)
        total_eaten = sum(log.calories for log in logs if log.calories)
        
        goal = user.profile.daily_calorie_goal

        return Response({
            "daily_goal": goal,
            "total_eaten": total_eaten,
            "remaining": (goal - total_eaten) if goal else 0
        })