from django.urls import path
from .views import FoodRecognitionAPIView,FoodNutritionAPIView,EatFoodAPIView,FoodLogListAPIView

urlpatterns = [
    path("recognize-food/", FoodRecognitionAPIView.as_view()),
    path("food-nutrition/", FoodNutritionAPIView.as_view(), name="food-nutrition"),
    path("eat-food/",EatFoodAPIView.as_view(),name="food-eat"),
    path("food-logs/", FoodLogListAPIView.as_view(), name="food-logs"),
]
