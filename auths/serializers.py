# auths/serializers.py
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import UserProfile
from utils.calculate_nutr import calculate_daily_calories

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    calories_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = (
            'age', 'gender', 'weight', 'height', 'goal', 'activity_level',
            'daily_calorie_goal', 'calories_consumed_today', 'calories_remaining'
        )
        read_only_fields = ('daily_calorie_goal', 'calories_consumed_today')
    
    def get_calories_remaining(self, obj):
        """Calculate remaining calories for today"""
        obj.reset_daily_calories_if_needed()
        if obj.daily_calorie_goal:
            return obj.daily_calorie_goal - obj.calories_consumed_today
        return 0
    
    def update(self, instance, validated_data):
        """Update profile and recalculate calorie goal"""
        # Update fields
        for field, value in validated_data.items():
            setattr(instance, field, value)
        
        # Recalculate daily calorie goal
        instance.recalculate_daily_goal()
        
        return instance


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)
    
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
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.username
        return token