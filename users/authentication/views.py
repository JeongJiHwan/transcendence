import requests
import jwt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from rest_framework.permissions import AllowAny
from django.shortcuts import redirect
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import OAuthCallbackQuerySerializer, OAuthUserSerializer
from .utils import TokenProvider

User = get_user_model()


class OAuthLogin42(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(tags=["oauth 로그인"], responses={200: openapi.Response("Redirect to 42 OAuth login page")})
    def get(self, request, *args, **kwargs):
        auth_url = f"{settings.AUTH_URL}?client_id={settings.CLIENT_ID}&redirect_uri={settings.REDIRECT_URI}&response_type=code&scope=public"
        return redirect(auth_url)


class OAuthCallback42(APIView):
    permission_classes = [AllowAny]  # 인증이 필요 없는 엔드포인트

    @swagger_auto_schema(tags=["oauth 로그인 후 처리"], query_serializer=OAuthCallbackQuerySerializer, responses={200: OAuthUserSerializer})
    def get(self, request, *args, **kwargs):
        code = request.GET.get('code')

        token_data = {
            'grant_type': 'authorization_code',
            'client_id': settings.CLIENT_ID,
            'client_secret': settings.CLIENT_SECRET,
            'code': code,
            'redirect_uri': settings.REDIRECT_URI,
        }

        # 42 API로 토큰 요청
        token_response = requests.post(settings.TOKEN_URL, data=token_data).json()
        access_token = token_response.get('access_token')

        if not access_token:
            return Response({'error': 'Invalid token response'}, status=status.HTTP_400_BAD_REQUEST)

        # 42 API로 사용자 정보 요청
        user_data_response = requests.get('https://api.intra.42.fr/v2/me', headers={
            'Authorization': f'Bearer {access_token}',
        }).json()

        if not user_data_response:
            return Response({'error': 'Invalid user data response'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            email = user_data_response['email']
            username = user_data_response['login']
            user, created = User.objects.get_or_create(
                email=email,
                username=username
            )
            user.save()
        except Exception as e:
            print(f"User creation failed: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 로그인 처리
        login(request, user)

        # Generate custom JWT with expiration time and refresh token
        jwt_token = TokenProvider.generate_jwt_token(user)
        refresh_token = TokenProvider.generate_refresh_token(user)

        # Serializer를 사용하여 Response 반환
        serializer = OAuthUserSerializer({
            'jwt_token': jwt_token,
            'user_id': user.id,
            'user_email': user.email,
            'username': user.username,
        })

        response = Response(serializer.data, status=status.HTTP_200_OK)
        TokenProvider.set_refresh_token_cookie(response, refresh_token)

        return response


class TokenRefresh(APIView):
    permission_classes = [AllowAny]  # 인증이 필요 없는 엔드포인트

    @swagger_auto_schema(tags=["토큰 재발급"], responses={200: OAuthUserSerializer})
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'error': 'No refresh token'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Refresh token expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.InvalidTokenError:
            return Response({'error': 'Invalid refresh token'}, status=status.HTTP_400_BAD_REQUEST)

        user_id = payload.get('user_id')
        user = User.objects.get(id=user_id)

        # Generate custom JWT with expiration time and refresh token
        jwt_token = TokenProvider.generate_jwt_token(user)
        refresh_token = TokenProvider.generate_refresh_token(user)

        serializer = OAuthUserSerializer({
            'jwt_token': jwt_token,
            'user_id': user.id,
            'user_email': user.email,
            'username': user.username,
        })

        response = Response(serializer.data, status=status.HTTP_200_OK)
        TokenProvider.set_refresh_token_cookie(response, refresh_token)
        return response