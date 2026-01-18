from django.db import models
from django.utils import timezone
from utils.enums import PortionType
from django.conf import settings

class FoodItem(models.Model):
    name = models.CharField(max_length=120, unique=True)
    portion_type = models.CharField(max_length=20, choices=PortionType.choices)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.strip().lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class FoodNutrition(models.Model):
    """
    Store either:
    - per_piece_* for COUNTABLE foods
    - *_small/medium/large for PORTION foods
    """
    food = models.OneToOneField(FoodItem, on_delete=models.CASCADE, related_name="nutrition")

    # COUNTABLE (per piece)
    calories_per_piece = models.FloatField(null=True, blank=True)
    protein_per_piece = models.FloatField(null=True, blank=True)
    carbs_per_piece = models.FloatField(null=True, blank=True)
    fat_per_piece = models.FloatField(null=True, blank=True)

    # PORTION (S/M/L)
    calories_small = models.FloatField(null=True, blank=True)
    protein_small = models.FloatField(null=True, blank=True)
    carbs_small = models.FloatField(null=True, blank=True)
    fat_small = models.FloatField(null=True, blank=True)

    calories_medium = models.FloatField(null=True, blank=True)
    protein_medium = models.FloatField(null=True, blank=True)
    carbs_medium = models.FloatField(null=True, blank=True)
    fat_medium = models.FloatField(null=True, blank=True)

    calories_large = models.FloatField(null=True, blank=True)
    protein_large = models.FloatField(null=True, blank=True)
    carbs_large = models.FloatField(null=True, blank=True)
    fat_large = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Nutrition: {self.food.name}"




class FoodLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="food_logs")
    image = models.ImageField(upload_to="food_detection/")

    food_item = models.ForeignKey(
        FoodItem,
        on_delete=models.PROTECT, 
        related_name="logs"
    )

    confidence = models.FloatField()

    pieces = models.FloatField(null=True, blank=True)
    size = models.CharField(max_length=10, null=True, blank=True)  # small/medium/large

    calories = models.FloatField(null=True, blank=True)
    protein = models.FloatField(null=True, blank=True)
    carbs = models.FloatField(null=True, blank=True)
    fat = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)    
    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.food_item.name} @ {self.created_at:%Y-%m-%d %H:%M}"
