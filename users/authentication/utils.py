from datetime import datetime, timedelta
from django.conf import settings
import jwt


class TokenGenerator:
    @staticmethod
    def generate_jwt_token(user):
        exp = datetime.now() + timedelta(days=1)
        payload = {
            'user_id': user.id,
            'user_email': user.email,
            'username': user.username,
            'exp': exp,
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        return token
