from django.urls import path
from .views import FriendRequest, AvatarUploadView, UserProfileView

urlpatterns = [
    path('friendship', FriendRequest.as_view(), name='friendship'),
    path('profile/avatar', AvatarUploadView.as_view(), name='avatar'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/<int:user_id>', UserProfileView.as_view(), name='profile'),
]