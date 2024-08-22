from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Friendship
from .serializers import FriendSerializer, FriendRequestSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

User = get_user_model()


class FriendRequest(APIView):
    permission_classes = [IsAuthenticated]  # 인증이 필요 없는 엔드포인트

    @swagger_auto_schema(tags=["친구 목록"], responses={200: FriendSerializer(many=True)})
    def get(self, request, *args, **kwargs):
        user = request.user

        # 사용자가 보낸 친구 요청을 가져오기
        friendships = Friendship.objects.filter(from_user=user)

        # 모든 세션 데이터를 한 번에 가져오기
        session_keys = [friend.to_user.id for friend in friendships]
        sessions = Session.objects.filter(session_key__in=session_keys, expire_date__gte=timezone.now())

        # 세션 데이터를 사전 형태로 저장
        session_dict = {session.session_key: session for session in sessions}

        # 결과 반환
        friend_list = []
        for friend in friendships:
            session = session_dict.get(friend.to_user.id)
            online_status = session is not None
            friend_data = {
                'id': friend.to_user.id,
                'username': friend.to_user.username,
                'email': friend.to_user.email,
                'online_status': online_status
            }
            # Serializer를 사용하여 데이터 직렬화
            serializer = FriendSerializer(friend_data)
            friend_list.append(serializer.data)

        return Response({'friends': friend_list})

    @swagger_auto_schema(tags=["친구 요청"], request_body=FriendRequestSerializer, responses={201: openapi.Response("Friend request sent successfully")})
    def post(self, request, *args, **kwargs):
        serializer = FriendRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                from_user = request.user
                to_user = serializer.validated_data['friend_id']
                Friendship.add_friend(from_user, to_user)
                return Response({'message': 'Friend request sent successfully'}, status=status.HTTP_201_CREATED)
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(tags=["친구 요청 취소"], request_body=FriendRequestSerializer, responses={204: openapi.Response("Friend request canceled successfully")})
    def delete(self, request, *args, **kwargs):
        serializer = FriendRequestSerializer(data=request.data)
        try:
            from_user_id = request.user.id
            to_user_id = serializer.validated_data['friend_id']

            from_user = User.objects.get(id=from_user_id)
            to_user = User.objects.get(id=to_user_id)

            friendship = Friendship.objects.get(from_user=from_user, to_user=to_user)
            friendship.delete()
        except User.DoesNotExist:
            return Response({'error': 'Friend User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except Friendship.DoesNotExist:
            return Response({'error': 'Friendship does not exist'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'message': 'Friendship deleted successfully'}, status=status.HTTP_204_NO_CONTENT)