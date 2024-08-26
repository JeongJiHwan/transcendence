from rest_framework import serializers
from django.shortcuts import get_object_or_404
from .models import EmailVerify


class OAuthCallbackQuerySerializer(serializers.Serializer):
    code = serializers.CharField()


class OAuthUserSerializer(serializers.Serializer):
    jwt_token = serializers.CharField()
    user_id = serializers.IntegerField()
    user_email = serializers.EmailField()
    username = serializers.CharField()


class VerificationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data.get('email')
        code = data.get('code')
        verify = get_object_or_404(EmailVerify, email=email)
        if code == verify.code:  # 인증코드 일치 여부 확인
            verify.delete()  # 인증코드 삭제
            return data
        else:
            raise serializers.ValidationError("Invalid verification code")