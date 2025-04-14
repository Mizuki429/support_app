from django.urls import path
from . import views

urlpatterns = [
    path("ask/", views.ask_concern, name="ask_concern"),
    path("confirm/", views.confirm_scene, name="confirm_scene"),
    path("strategy/", views.ask_custom_strategy, name="ask_custom_strategy"),
    path("support-need/", views.ask_support, name="ask_support"),
    path("ideal/", views.ask_ideal, name="ask_ideal"),
    path("summary/", views.summary, name="summary"),
]
