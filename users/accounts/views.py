from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from .models import Friendship
from .serializers import UserSerializer, FriendSerializer, FriendRequestSerializer, AvatarUploadSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

User = get_user_model()


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["프로필"],
        operation_description='유저 프로필 조회 (자신 또는 다른 사용자)',
        responses={200: UserSerializer}
    )
    def get(self, request, user_id=None, *args, **kwargs):
        if user_id:
            # 다른 사용자의 정보를 가져오기 위해 user_id를 사용하여 User 인스턴스를 가져옴
            user = get_object_or_404(User, pk=user_id)
        else:
            # user_id가 제공되지 않은 경우 현재 사용자의 정보를 가져옴
            user = request.user

        serializer = UserSerializer(instance=user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class FriendRequest(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["친구 관리 기능"], operation_description='친구 목록 조회', responses={200: FriendSerializer(many=True)})
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

    @swagger_auto_schema(tags=["친구 관리 기능"], operatio_description='친구 추가', request_body=FriendRequestSerializer, responses={201: openapi.Response("Friend request sent successfully")})
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

    @swagger_auto_schema(tags=["친구 관리 기능"], operation_description='친구 삭제', request_body=FriendRequestSerializer, responses={204: openapi.Response("Friend request canceled successfully")})
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


class AvatarUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        tags=["프로필"],
        operation_description='아바타 업로드',
        request_body=AvatarUploadSerializer,
        responses={200: openapi.Response("Avatar uploaded successfully")}
    )
    def post(self, request, *args, **kwargs):
        user = request.user

        serializer = AvatarUploadSerializer(data=request.data)
        if serializer.is_valid():
            avatar_file = serializer.validated_data['avatar']

            # 아바타 업데이트
            user.avatar = avatar_file
            user.save()

            return Response({'message': 'Avatar uploaded successfully'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)