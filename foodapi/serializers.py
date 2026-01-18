from rest_framework import serializers
from django.shortcuts import get_object_or_404
from .models import FoodLog, FoodItem
from utils.enums import PortionType
from utils.calculate_nutr import compute_nutrition
from urllib.parse import urlparse, unquote
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

class FoodNutritionRequestSerializer(serializers.Serializer):
    food = serializers.CharField(max_length=120)
    pieces = serializers.FloatField(required=False, min_value=0.1)
    size = serializers.ChoiceField(required=False, choices=["small", "medium", "large"])

    def validate_food(self, value: str):
        return value.strip().lower()

    def validate(self, attrs):

        if not attrs.get("pieces") and not attrs.get("size"):
            raise serializers.ValidationError(
                {"detail": "Provide either 'pieces' (for countable foods) or 'size' (small/medium/large)."}
            )
        return attrs


class FoodLogCreateSerializer(serializers.ModelSerializer):
    """
    Used when user presses EAT
    """
    food = serializers.CharField(write_only=True)
    image_url = serializers.URLField(write_only=True)
    pieces = serializers.FloatField(required=False)
    size = serializers.ChoiceField(
        choices=["small", "medium", "large"],
        required=False
    )
    image = serializers.ImageField(read_only=True)

    class Meta:
        model = FoodLog
        fields = [
            "id",
            "image",
            "image_url",
            "food",
            "confidence",
            "pieces",
            "size",
            "calories",
            "protein",
            "carbs",
            "fat",
            "created_at",
        ]
        read_only_fields = [
            "calories",
            "protein",
            "carbs",
            "fat",
            "created_at",
        ]

    def validate_food(self, value):
        return value.strip().lower()

    def validate(self, attrs):
        food_name = attrs.get("food")
        pieces = attrs.get("pieces")
        size = attrs.get("size")

        food_item = get_object_or_404(FoodItem, name=food_name, is_active=True)

        if food_item.portion_type == PortionType.COUNTABLE and pieces is None:
            raise serializers.ValidationError(
                {"pieces": "This food requires number of pieces."}
            )

        if food_item.portion_type == PortionType.PORTION and not size:
            raise serializers.ValidationError(
                {"size": "This food requires portion size (small/medium/large)."}
            )

        attrs["food_item"] = food_item
        return attrs


    def create(self, validated_data):
        request = self.context["request"]

        food_item = validated_data.pop("food_item")
        validated_data.pop("food")
        image_url = validated_data.pop("image_url")

        # 🔹 convert image_url → ImageField
        parsed = urlparse(image_url)
        relative_path = parsed.path.replace("/media/", "")
        relative_path = unquote(relative_path)  # ✅ converts %20 to space
        if not default_storage.exists(relative_path):
            raise serializers.ValidationError(
                {"image_url": "Image not found on server."}
            )

        with default_storage.open(relative_path, "rb") as f:
            image_file = ContentFile(f.read(), name=relative_path.split("/")[-1])

        nutrition = food_item.nutrition
        pieces = validated_data.get("pieces")
        size = validated_data.get("size")

        result = compute_nutrition(food_item, pieces=pieces, size=size)

        validated_data.update({
            "user": request.user,
            "food_item": food_item,
            "image": image_file,
            "calories": result["calories"],
            "protein": result["protein"],
            "carbs": result["carbs"],
            "fat": result["fat"],
        })

        return super().create(validated_data)

# for get api
class FoodLogSerializer(serializers.ModelSerializer):
    food = serializers.CharField(source="food_item.name", read_only=True)

    class Meta:
        model = FoodLog
        fields = [
            "id", "image", "food", "confidence", "pieces", "size",
            "calories", "protein", "carbs", "fat", "created_at"
        ]