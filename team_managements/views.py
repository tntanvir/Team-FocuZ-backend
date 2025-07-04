from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Team
from .serializers import TeamSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
class TeamListView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        teams = Team.objects.all()
        serializer = TeamSerializer(teams, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TeamSerializer(data=request.data)
        if serializer.is_valid():
            team = serializer.save()
            return Response(TeamSerializer(team).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class TeamDetailView(APIView):
    # permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Team.objects.get(pk=pk)
        except Team.DoesNotExist:
            return None

    def get(self, request, pk):
        team = self.get_object(pk)
        if team is None:
            return Response({"error": "Team not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = TeamSerializer(team)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        team = self.get_object(pk)
        if team is None:
            return Response({"error": "Team not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = TeamSerializer(team, data=request.data)
        if serializer.is_valid():
            updated_team = serializer.save()
            return Response(TeamSerializer(updated_team).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        team = self.get_object(pk)
        if team is None:
            return Response({"error": "Team not found"}, status=status.HTTP_404_NOT_FOUND)
        team.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Create your views here.
