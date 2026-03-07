"""
Import URL routing.
"""

from django.urls import path

from . import views

urlpatterns = [
    path(
        "training-program/",
        views.ImportViewSet.as_view({"post": "upload"}),
    ),
    path(
        "<uuid:pk>/status/",
        views.ImportViewSet.as_view({"get": "status_check"}),
    ),
    path(
        "<uuid:pk>/preview/",
        views.ImportViewSet.as_view({"get": "preview"}),
    ),
    path(
        "<uuid:pk>/confirm/",
        views.ImportViewSet.as_view({"post": "confirm"}),
    ),
]
