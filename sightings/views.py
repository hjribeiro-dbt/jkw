from rest_framework import generics

from .models import JKWSighting
from .serializers import JKWSightingSerializer


class JKWSightingCreateView(generics.CreateAPIView):
    queryset = JKWSighting.objects.all()
    serializer_class = JKWSightingSerializer