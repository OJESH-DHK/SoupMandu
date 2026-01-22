# auths/models.py
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
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
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
    
    # ✅ NEW: Track consumed calories for today
    calories_consumed_today = models.FloatField(default=0)
    last_reset_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Profile for {self.user.username}"
    
    def recalculate_daily_goal(self):
        """Recalculate and save daily calorie goal"""
        from utils.calculate_nutr import calculate_daily_calories
        
        self.daily_calorie_goal = calculate_daily_calories(
            age=self.age,
            gender=self.gender,
            weight=self.weight,
            height=self.height,
            activity_level=self.activity_level,
            goal=self.goal
        )
        self.save(update_fields=['daily_calorie_goal'])
    
    def reset_daily_calories_if_needed(self):
        """Reset daily calorie counter if it's a new day"""
        from django.utils import timezone
        today = timezone.localdate()
        
        if self.last_reset_date != today:
            self.calories_consumed_today = 0
            self.last_reset_date = today
            self.save(update_fields=['calories_consumed_today', 'last_reset_date'])
    
    def add_calories(self, calories):
        """Add calories to today's total"""
        self.reset_daily_calories_if_needed()
        self.calories_consumed_today += calories
        self.save(update_fields=['calories_consumed_today'])