from rest_framework import generics

from .models import JKWSighting
from .serializers import JKWSightingSerializer


class JKWSightingListCreateView(generics.ListCreateAPIView):
    queryset = JKWSighting.objects.all().order_by("-created_at")
    serializer_class = JKWSightingSerializer