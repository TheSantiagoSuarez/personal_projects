from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("points", views.points, name="points"),
    path("players", views.players, name="players"),
    path("draft", views.draft, name="draft")
]
