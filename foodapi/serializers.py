from rest_framework import serializers


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
