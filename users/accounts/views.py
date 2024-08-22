from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from .models import Friendship

User = get_user_model()


class FriendRequest(APIView):
    permission_classes = [IsAuthenticated]  # 인증이 필요 없는 엔드포인트

    def get(self, request, *args, **kwargs):
        user = request.user

        # 사용자가 보낸 친구 요청을 가져오기
        friends = list(Friendship.objects.filter(from_user=user))

        # 결과 반환
        friend_list = [
            {'id': friend.to_user.id, 'username': friend.to_user.username, 'email': friend.to_user.email}
            for friend in friends
        ]

        return Response({'friends': friend_list})

    def post(self, request, *args, **kwargs):
        try:
            from_user_id = request.user.id
            to_user_id = request.data.get('friend_id')

            from_user = User.objects.get(id=from_user_id)
            to_user = User.objects.get(id=to_user_id)

            Friendship.add_friend(from_user, to_user)
        except User.DoesNotExist:
            return Response({'error': 'Friend User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Friend request sent successfully'}, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        try:
            from_user_id = request.user.id
            to_user_id = request.data.get('friend_id')

            from_user = User.objects.get(id=from_user_id)
            to_user = User.objects.get(id=to_user_id)

            friendship = Friendship.objects.get(from_user=from_user, to_user=to_user)
            friendship.delete()
        except User.DoesNotExist:
            return Response({'error': 'Friend User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except Friendship.DoesNotExist:
            return Response({'error': 'Friendship does not exist'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'message': 'Friendship deleted successfully'}, status=status.HTTP_204_NO_CONTENT)