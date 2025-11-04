from django.urls import path
from .views import PopupImageView

urlpatterns = [
    path('popup-images/', PopupImageView.as_view(), name='popup-images'),
]