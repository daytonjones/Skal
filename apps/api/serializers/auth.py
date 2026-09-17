from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

from apps.accounts.models import UserNotificationPrefs

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )


class NotificationPrefsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotificationPrefs
        fields = [
            "email_notifications",
            "notify_tosna",
            "notify_sg_check",
            "notify_rack",
            "notify_bottle",
        ]


class MeSerializer(serializers.ModelSerializer):
    notification_prefs = NotificationPrefsSerializer(required=False)

    class Meta:
        model = User
        fields = ["id", "username", "email", "theme", "is_approved", "notification_prefs"]
        read_only_fields = ["id", "username", "is_approved"]

    def update(self, instance, validated_data):
        prefs_data = validated_data.pop("notification_prefs", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if prefs_data is not None:
            prefs, _ = UserNotificationPrefs.objects.get_or_create(user=instance)
            for attr, value in prefs_data.items():
                setattr(prefs, attr, value)
            prefs.save()
        return instance
