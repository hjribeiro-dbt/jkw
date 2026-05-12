from django.urls import path

from .views import JKWSightingListCreateView, LoginView

urlpatterns = [
    path("sightings/", JKWSightingListCreateView.as_view(), name="list-create-sightings"),
    path("login/", LoginView.as_view(), name="login"),
]