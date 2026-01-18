from django.urls import path
from .views import FoodRecognitionAPIView,FoodNutritionAPIView

urlpatterns = [
    path("recognize-food/", FoodRecognitionAPIView.as_view()),
    path("food-nutrition/", FoodNutritionAPIView.as_view(), name="food-nutrition"),
]
