from django.urls import path
from .views import (
    FoodRecognitionAPIView, 
    FoodNutritionAPIView, 
    EatFoodAPIView, 
    FoodLogListAPIView,
    DailySummaryAPIView  
)

urlpatterns = [
    path("recognize-food/", FoodRecognitionAPIView.as_view(), name="recognize"),
    path("food-nutrition/", FoodNutritionAPIView.as_view(), name="nutrition"),
    path("eat-food/", EatFoodAPIView.as_view(), name="eat"),
    path("food-logs/", FoodLogListAPIView.as_view(), name="logs"),
    path("daily-summary/", DailySummaryAPIView.as_view(), name="summary"),
]