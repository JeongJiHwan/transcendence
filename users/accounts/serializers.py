from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'avatar']

    def get_avatar(self, obj):
        if obj.avatar and hasattr(obj.avatar, 'url'):
            return self.context['request'].build_absolute_uri(obj.avatar.url)
        return None

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if ret['avatar'] is None:
            ret['avatar'] = None  # Ensure that if avatar is None, it is explicitly set to None
        return ret


class FriendSerializer(serializers.Serializer):
    online_status = serializers.BooleanField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'online_status']

    def to_representation(self, instance):
        # Override to include online_status in representation
        representation = super().to_representation(instance)
        representation['online_status'] = self.context['online_status'][instance.id]
        return representation


class FriendRequestSerializer(serializers.Serializer):
    friend_id = serializers.IntegerField()

    def validate_friend_id(self, value):
        if value == self.context['request'].user.id:
            raise serializers.ValidationError('You cannot send a friend request to yourself')
        return value


class AvatarUploadSerializer(serializers.Serializer):
    avatar = serializers.FileField()