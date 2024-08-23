from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserProfileSerializer(serializers.Serializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'avatar']

    def get_avatar(self, obj):
        if obj.avatar:
            return self.context['request'].build_absolute_uri(obj.avatar.url)
        return None

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['id'] = instance.user.id
        ret['username'] = instance.user.username
        ret['email'] = instance.user.email
        return ret


class FriendSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    online_status = serializers.BooleanField()


class FriendRequestSerializer(serializers.Serializer):
    friend_id = serializers.IntegerField()

    def validate_friend_id(self, value):
        if value == self.context['request'].user.id:
            raise serializers.ValidationError('You cannot send a friend request to yourself')
        return value


class AvatarUploadSerializer(serializers.Serializer):
    avatar = serializers.FileField()