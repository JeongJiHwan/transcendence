from rest_framework import serializers


class OAuthCallbackQuerySerializer(serializers.Serializer):
    code = serializers.CharField()


class OAuthUserSerializer(serializers.Serializer):
    jwt_token = serializers.CharField()
    user_id = serializers.IntegerField()
    user_email = serializers.EmailField()
    username = serializers.CharField()
    expires_in = serializers.DateTimeField()