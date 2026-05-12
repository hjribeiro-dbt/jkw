from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import JKWSighting


class JKWSightingSerializer(serializers.ModelSerializer):
    class Meta:
        model = JKWSighting
        fields = [
            "id",
            "latitude",
            "longitude",
            "description",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_latitude(self, value):
        if value < -90 or value > 90:
            raise serializers.ValidationError("Latitude must be between -90 and 90.")
        return value

    def validate_longitude(self, value):
        if value < -180 or value > 180:
            raise serializers.ValidationError("Longitude must be between -180 and 180.")
        return value


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True, trim_whitespace=False)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")
        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError({"non_field_errors": ["Invalid username or password."]})
        attrs["user"] = user
        return attrs