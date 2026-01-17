from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ultralytics import YOLO
from PIL import Image
import io
from rest_framework.permissions import AllowAny
# Load model ONCE (important for performance)
MODEL_PATH = "models/best.pt"
model = YOLO(MODEL_PATH)

class FoodRecognitionAPIView(APIView):
    """
    POST image -> returns predicted food name and confidence
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

            # YOLOv8 classification output
            probs = results[0].probs
            top_index = probs.top1
            confidence = float(probs.top1conf)
            label = model.names[top_index]

            return Response({
                "food": label,
                "confidence": round(confidence, 4)
            })

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
