from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import UserProfile
from utils.calculate_nutr import calculate_daily_calories

User = get_user_model()




class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('age', 'gender', 'weight', 'height', 'goal', 'activity_level')

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)
    
    # Include profile fields
    profile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "password2", "profile")

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        validated_data.pop("password2")
        password = validated_data.pop("password")
        
        # Create User
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # Calculate Calories
        cal_goal = calculate_daily_calories(
            age=profile_data['age'],
            gender=profile_data['gender'],
            weight=profile_data['weight'],
            height=profile_data['height'],
            activity_level=profile_data['activity_level'],
            goal=profile_data['goal']
        )

        # Create Profile
        UserProfile.objects.create(user=user, daily_calorie_goal=cal_goal, **profile_data)
        
        return user


class LoginSerializer(TokenObtainPairSerializer):
    """
    Returns access + refresh tokens.
    You can add extra fields into response if you want.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # optional custom claims:
        token["username"] = user.username
        return token
