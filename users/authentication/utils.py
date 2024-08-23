from datetime import datetime, timedelta
from django.conf import settings
import jwt


class TokenProvider:
    @staticmethod
    def generate_jwt_token(user):
        exp = datetime.now() + timedelta(seconds=settings.JWT_TOKEN_EXPIRATION)
        payload = {
            'user_id': user.id,
            'user_email': user.email,
            'username': user.username,
            'exp': exp,
        }
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256')
        return token

    @staticmethod
    def generate_refresh_token(user):
        exp = datetime.now() + timedelta(seconds=settings.REFRESH_TOKEN_EXPIRATION)
        payload = {
            'user_id': user.id,
            'exp': exp,
        }
        token = jwt.encode(payload, settings.REFRESH_SECRET, algorithm='HS256')
        return token


    @staticmethod
    def set_refresh_token_cookie(response, refresh_token):
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            max_age=settings.REFRESH_TOKEN_EXPIRATION,  # 쿠키 만료 시간 설정
            # secure=True,  # HTTPS 연결에서만 쿠키 전송
            httponly=True,  # JavaScript에서 쿠키 접근 불가능
            samesite='Strict'  # CSRF 공격 방지를 위해 SameSite 설정
        )
