from django.urls import path
from .views import FriendRequest, AvatarUploadView

urlpatterns = [
    path('friendship', FriendRequest.as_view(), name='friendship'),
    path('profile/avatar', AvatarUploadView.as_view(), name='avatar'),
]