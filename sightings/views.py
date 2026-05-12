from django.contrib.auth import login as auth_login
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import JKWSighting
from .serializers import JKWSightingSerializer, LoginSerializer


class JKWSightingListCreateView(generics.ListCreateAPIView):
    queryset = JKWSighting.objects.all().order_by("-created_at")
    serializer_class = JKWSightingSerializer


class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []  # avoid CSRF requirement from SessionAuthentication for login

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        auth_login(request, user)
        data = {
            "id": user.id,
            "username": user.get_username(),
            "email": user.email,
        }
        return Response(data, status=status.HTTP_200_OK)