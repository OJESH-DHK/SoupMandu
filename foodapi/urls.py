from django.urls import path
from .views import FoodRecognitionAPIView

urlpatterns = [
    path("recognize-food/", FoodRecognitionAPIView.as_view()),
]
