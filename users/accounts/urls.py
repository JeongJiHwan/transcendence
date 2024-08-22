from django.urls import path
from .views import FriendRequest

urlpatterns = [
    path('friendship', FriendRequest.as_view(), name='friendship'),
]