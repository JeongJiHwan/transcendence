from rest_framework import serializers


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