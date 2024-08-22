from django.urls import path
from .views import OAuthCallback42, OAuthLogin42

urlpatterns = [
    path('login42', OAuthLogin42.as_view(), name='42oauth_login'),
    path('callback42', OAuthCallback42.as_view(), name='42oauth_callback'),
]