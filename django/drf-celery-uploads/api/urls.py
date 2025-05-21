# api/urls.py
from django.urls import path
from .views import hello_world, upload_csv

urlpatterns = [
    path('hello/', hello_world),
    path('upload-csv/', upload_csv),
]
