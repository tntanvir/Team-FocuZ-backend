# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from django.utils.timezone import now
from datetime import timedelta
from .models import  Media, DailyReport, WeeklyReport, MonthlyReport
from .serializers import MediaSerializer
from rest_framework.exceptions import ValidationError
from team_managements.models import Team
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser


# class MediaPagination(PageNumberPagination):
#     page_size = 9  # Set the number of items per page
#     page_size_query_param = 'page_size'  # Allows the user to specify a custom page size (optional)
#     max_page_size = 100  # Optional: to limit the maximum number of items per page

# class MediaView(APIView):
#     permission_classes = [IsAuthenticated]  
   



#     def get(self, request):
#         user = request.user

#         # Check if the user is authenticated
#         if user.is_authenticated:
#             # Check if the user is an admin (using is_staff for simplicity)
#             if user.is_staff:  # Admins should have is_staff set to True
#                 # Admin can see all media files
#                 media = Media.objects.all().order_by('-uploaded_at')
#             else:
#                 # Get the teams the current user is part of
#                 user_teams = Team.objects.filter(users=user)

#                 # Get the names of the teams the user is part of
#                 team_names = [team.name for team in user_teams]

#                 # Fetch all media related to the user's teams
#                 team_media = Media.objects.filter(team__in=team_names).order_by('-uploaded_at')

#                 # Combine all team media for the user
#                 media = team_media

#             # Apply pagination to the media queryset
#             paginator = MediaPagination()
#             paginated_media = paginator.paginate_queryset(media, request)

#             # Serialize the paginated media data
#             serializer = MediaSerializer(paginated_media, many=True)

#             # Return the paginated response
#             return paginator.get_paginated_response(serializer.data)

#         else:
#             # If the user is not authenticated, return a 401 Unauthorized response
#             return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

# class MediaPagination(PageNumberPagination):
#     page_size = 9  # Set the number of items per page
#     page_size_query_param = 'page_size'  # Allows the user to specify a custom page size (optional)
#     max_page_size = 100  # Optional: to limit the maximum number of items per page

# class MediaView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user

#         # Filter query parameters for team name and category
#         team_filter = request.query_params.get('team', None)
#         category_filter = request.query_params.get('category', None)

#         # Check if the user is authenticated
#         if user.is_authenticated:
#             if user.is_staff:  # Admins can view all media
#                 media = Media.objects.all().order_by('-uploaded_at')
#             else:
#                 # Get the teams the current user is part of
#                 user_teams = Team.objects.filter(users=user)
#                 team_names = [team.name for team in user_teams]
#                 media = Media.objects.filter(team__in=team_names).order_by('-uploaded_at')

#             # Apply team filter if provided
#             if team_filter:
#                 media = media.filter(team__name=team_filter)

#             # Apply category filter if provided (e.g., "video", "audio", etc.)
#             if category_filter:
#                 media = media.filter(tag=category_filter)

#             # Apply pagination to the media queryset
#             paginator = MediaPagination()
#             paginated_media = paginator.paginate_queryset(media, request)

#             # Serialize the paginated media data
#             serializer = MediaSerializer(paginated_media, many=True)

#             # Return the paginated response
#             return paginator.get_paginated_response(serializer.data)

#         else:
#             # If the user is not authenticated, return a 401 Unauthorized response
#             return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
class MediaPagination(PageNumberPagination):
    page_size = 9  # Set the number of items per page
    page_size_query_param = 'page_size'  # Allows the user to specify a custom page size (optional)
    max_page_size = 100  # Optional: to limit the maximum number of items per page

class MediaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Filter query parameters for team name and category
        team_filter = request.query_params.get('team', None)
        category_filter = request.query_params.get('category', None)

        # Check if the user is authenticated
        if user.is_authenticated:
            if user.is_staff:  # Admins can view all media
                media = Media.objects.all().order_by('-uploaded_at')
            else:
                # Get the teams the current user is part of
                user_teams = Team.objects.filter(users=user)
                team_names = [team.name for team in user_teams]
                media = Media.objects.filter(team__in=team_names).order_by('-uploaded_at')

            # Apply team filter if provided
            if team_filter and team_filter != "All Teams":
                media = media.filter(team=team_filter)

            # Apply category filter if provided (e.g., "video", "audio", etc.)
            if category_filter and category_filter != "All":
                media = media.filter(tag=category_filter)

            # Apply pagination to the media queryset
            paginator = MediaPagination()
            paginated_media = paginator.paginate_queryset(media, request)

            # Serialize the paginated media data
            serializer = MediaSerializer(paginated_media, many=True)

            # Return the paginated response
            return paginator.get_paginated_response(serializer.data)

        else:
            # If the user is not authenticated, return a 401 Unauthorized response
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

   
    def post(self, request):
        user = request.user
        file_url = request.data.get('file')
        title = request.data.get('title')
        tag = request.data.get('tag')
        team = request.data.get('team')

        # Ensure all fields are provided and valid
        if not file_url or not title or not tag:
            return Response({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

        # Check the file extension based on role
        role = user.role
        if role == 'script writer' and not file_url.endswith('.txt'):
            return Response({"error": "Script Writers can only upload text files."}, status=status.HTTP_400_BAD_REQUEST)
        elif role == 'voice artist' and not file_url.endswith(('.mp3', '.wav', '.aac')):
            return Response({"error": "Voice Artists can only upload audio files."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the Media object and save
        media_payload = {
            'user': user.id,
            'title': title,
            'tag': tag,
            'file': file_url,
            'team': team if team else None,  
        }

        serializer = MediaSerializer(data=media_payload)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        data = Media.objects.get(pk=pk)
        serializer = MediaSerializer(data, request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, pk):
        data = Media.objects.get(pk=pk)
        if not data:
            return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)
        data.delete()
        return Response({"message": "File deleted successfully"}, status=status.HTTP_204_NO_CONTENT)






class FileUploadReportView(APIView):
    def get(self, request):
        today = now().date()

        # 📅 Daily Reports (last 7 days)
        last_7_days = [today - timedelta(days=i) for i in range(7)]
        daily_data = {
            str(day): DailyReport.objects.filter(date=day).first().file_count
            if DailyReport.objects.filter(date=day).exists() else 0
            for day in reversed(last_7_days)
        }

        # 📈 Weekly Reports (last 6 weeks)
        weekly_reports = WeeklyReport.objects.order_by('-week')[:6]
        weekly_data = {report.week: report.file_count for report in reversed(weekly_reports)}

        # 📊 Monthly Reports (last 6 months)
        monthly_reports = MonthlyReport.objects.order_by('-month')[:6]
        monthly_data = {report.month: report.file_count for report in reversed(monthly_reports)}

        return Response({
            "daily": daily_data,
            "weekly": weekly_data,
            "monthly": monthly_data,
        }, status=status.HTTP_200_OK)




