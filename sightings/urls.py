from django.urls import path

from .views import JKWSightingCreateView

urlpatterns = [
    path("sightings/", JKWSightingCreateView.as_view(), name="create-sighting"),
]