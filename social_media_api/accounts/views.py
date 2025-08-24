from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserSerializer
from rest_framework import permissions, generics, status
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .serializers import MiniUserSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

class LoginView(generics.GenericAPIView):
    def post(self, request):
        username = request.data.get('username')
        password= request.data.get('password')
        user = authenticate(username=username, password = password)

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response({'error': 'Invalid credentials'}, status=400)


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user




class FollowUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        target = get_object_or_404(User, pk=user_id)
        if target == request.user:
            return Response({"detail": "You cannot follow yourself."}, status=400)
        request.user.following.add(target)
        return Response({"detail": f"You are now following {target.username}."}, status=200)

class UnfollowUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        target = get_object_or_404(User, pk=user_id)
        if target == request.user:
            return Response({"detail": "You cannot unfollow yourself."}, status=400)
        request.user.following.remove(target)
        return Response({"detail": f"You unfollowed {target.username}."}, status=200)

class FollowersListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = MiniUserSerializer

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs['user_id'])
        return user.followers.all()

class FollowingListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = MiniUserSerializer

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs['user_id'])
        return user.following.all()
