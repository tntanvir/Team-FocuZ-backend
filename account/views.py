
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.views import APIView
from rest_framework import status
from .serializers import RegisterUserSerializer, CustomUserSerializer,UserRoleUpdateSerializer
from .models import CustomUser
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import TeamMembershipSerializer
from team_managements.models import Team


# Create your views here.

class RegisterUserView(APIView):
    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User registered successfully", "user": CustomUserSerializer(user).data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginUserView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate( username=username, password=password)
        if user is not None:
            token = RefreshToken.for_user(user)
            login(request, user)
            return Response({
                "message": "Login successful",
                "user": CustomUserSerializer(user).data,
                "refresh": str(token),
                "access": str(token.access_token)
            }, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    
class LogoutUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        tokenr  = request.data.get('token')
        if tokenr:
            try:
                token = RefreshToken(tokenr)
                token.blacklist()
                logout(request)
                return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "No token provided"}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = CustomUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    




class AllUsersView(APIView):
    # permission_classes = [IsAdminUser]

    def get(self, request, user_id=None):
        if user_id:
            try:
                user = CustomUser.objects.get(id=user_id)
                serializer = CustomUserSerializer(user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except CustomUser.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            users = CustomUser.objects.all()
            serializer = CustomUserSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
            user.delete()
            return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    # def patch(self, request, user_id):
    #     try:
    #         user = CustomUser.objects.get(id=user_id)
    #         serializer = UserRoleUpdateSerializer(user, data=request.data, partial=True)
    #         if serializer.is_valid():
    #             serializer.save()
    #             return Response({"message": "User role updated successfully"}, status=status.HTTP_200_OK)
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #     except CustomUser.DoesNotExist:
    #         return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    def patch(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "ইউজার খুঁজে পাওয়া যায়নি"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserRoleUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            updated_user = serializer.save()
            
            # যদি ম্যানেজার হিসেবে সেট করা হয় তাহলে টিম আপডেট করো (যদি team_id থাকে)
            team_id = request.data.get('team_id')
            if updated_user.role == 'manager' and team_id:
                try:
                    team = Team.objects.get(id=team_id)
                    team.manager = updated_user
                    team.save()
                except Team.DoesNotExist:
                    return Response({"error": "টিম খুঁজে পাওয়া যায়নি"}, status=404)

            return Response({
                "message": "ইউজারের তথ্য সফলভাবে আপডেট হয়েছে",
                "user": CustomUserSerializer(updated_user).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeamMembershipUpdateView(APIView):
    # permission_classes = [IsAuthenticated, IsAdminUser]

    def patch(self, request, team_id):
        try:
            team = Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            return Response({"error": "Team not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = TeamMembershipSerializer(team, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Team updated successfully", "team": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)