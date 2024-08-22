import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from django.conf import settings


User = get_user_model()


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split()[1]

        try:
            # JWT를 검증하고 페이로드를 디코딩
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

            # 페이로드에서 사용자 정보 추출
            user_id = payload['user_id']
            user = User.objects.get(id=user_id)

            return user, token

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token expired')

        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')

    def authenticate_header(self, request):
        return 'Bearer'
