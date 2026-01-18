from django.db import models

class PortionType(models.TextChoices):
    COUNTABLE = "COUNTABLE", "Countable (pieces)"
    PORTION = "PORTION", "Portion (S/M/L)"


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
