from django.urls import path

from .views import JKWSightingListCreateView

urlpatterns = [
    path("sightings/", JKWSightingListCreateView.as_view(), name="list-create-sightings"),
]