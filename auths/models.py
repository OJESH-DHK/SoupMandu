from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class UserProfile(models.Model):
    GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female')]
    GOAL_CHOICES = [
        ('Lose Weight', 'Lose Weight'),
        ('Gain Weight', 'Gain Weight'),
        ('Muscle Mass Gain', 'Muscle Mass Gain'),
        ('Shape Body', 'Shape Body'),
        ('Other', 'Other'),
    ]
    ACTIVITY_CHOICES = [
        ('Beginner', 'Beginner'), # 1.2
        ('Intermediate', 'Intermediate'), # 1.55
        ('Advanced', 'Advanced'), # 1.9
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    weight = models.FloatField(help_text="Weight in KG")
    height = models.FloatField(help_text="Height in CM")
    goal = models.CharField(max_length=30, choices=GOAL_CHOICES)
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)
    
    # Calculated daily target
    daily_calorie_goal = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Profile for {self.user.username}"