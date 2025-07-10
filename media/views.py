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
from django.utils import timezone
from account.serializers import CustomUserSerializer

class MediaPagination(PageNumberPagination):
    page_size = 9  # Set the number of items per page
    page_size_query_param = 'page_size'  # Allows the user to specify a custom page size (optional)
    max_page_size = 100  # Optional: to limit the maximum number of items per page

class MediaView(APIView):
    permission_classes = [IsAuthenticated]

    # def get(self, request):
    #     user = request.user

    #     # Filter query parameters for team name and category
    #     team_filter = request.query_params.get('team', None)
    #     category_filter = request.query_params.get('category', None)

    #     # Check if the user is authenticated
    #     if user.is_authenticated:
    #         # Initialize the media queryset
    #         media = Media.objects.all().order_by('-uploaded_at')

    #         # Access control based on the user's role
    #         if user.is_staff:  # Super Admin
    #             # Super Admin can see all media
    #             pass
    #         elif user.role == "video editor":
    #             # Video Editor should only see posts from the Super Admin for their team
    #             media = media.filter(
    #                 tag__in=['video', 'script', 'voice'],  # Allow Video, Script, and Voice media
    #                 team__in=[team.name for team in Team.objects.filter(users=user)]  # Media from teams they belong to
    #             )
    #             # Video Editor can only see posts from the Super Admin for their team
    #             media = media.filter(user__role="admin")
    #         elif user.role == "script writer":
    #             # Script Writer can see media tagged as 'script' for their teams
    #             media = media.filter(
    #                 tag='script',
    #                 team__in=[team.name for team in Team.objects.filter(users=user)]
    #             )
    #         elif user.role == "voice artist":
    #             # Voice Artist can see media tagged as 'voice' for their teams
    #             media = media.filter(
    #                 tag='voice',
    #                 team__in=[team.name for team in Team.objects.filter(users=user)]
    #             )
    #         else:
    #             # If user role is not recognized, return empty result
    #             media = media.none()

    #         # Apply team filter if provided
    #         if team_filter and team_filter != "All Teams":
    #             media = media.filter(team=team_filter)

    #         # Apply category filter if provided (e.g., "video", "audio", etc.)
    #         if category_filter and category_filter != "All":
    #             media = media.filter(tag=category_filter)

    #         # Apply pagination to the media queryset
    #         paginator = MediaPagination()
    #         paginated_media = paginator.paginate_queryset(media, request)

    #         # Serialize the paginated media data
    #         serializer = MediaSerializer(paginated_media, many=True)

    #         # Return the paginated response
    #         return paginator.get_paginated_response(serializer.data)

    #     else:
    #         # If the user is not authenticated, return a 401 Unauthorized response
    #         return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
    def get(self, request):
        user = request.user

        # Filter query parameters for team name and category
        team_filter = request.query_params.get('team', None)
        category_filter = request.query_params.get('category', None)

        # Check if the user is authenticated
        if user.is_authenticated:
            # Initialize the media queryset
            media = Media.objects.all().order_by('-uploaded_at')

            # Access control based on the user's role
            if user.is_staff:  # Super Admin
                # Super Admin can see all media
                pass
            elif user.role == "video editor":
                # Video Editor can only see Super Admin's posts
                media = media.filter(
                    team__in=[team.name for team in Team.objects.filter(users=user)],
                    user__role="admin"  # Only see posts made by Super Admin
                )
            elif user.role == "script writer":
                # Script Writer can see Super Admin's, Video Editor's, and Voice Artist's posts
                media = media.filter(
                    team__in=[team.name for team in Team.objects.filter(users=user)],
                    tag__in=['video', 'script', 'voice'],  # Script Writer can see all media types
                )
                # Exclude their own posts (Script Writer's posts)
                media = media.exclude(user__role="script writer")
            elif user.role == "voice artist":
                # Voice Artist can see Super Admin's and Video Editor's posts
                media = media.filter(
                    team__in=[team.name for team in Team.objects.filter(users=user)],
                    tag__in=['video', 'voice','script'],  # Voice Artist can see video and voice media
                )
                # Exclude Script Writer's posts
                media = media.exclude(user__role="script writer")
                # Exclude their own posts (Voice Artist's posts)
                media = media.exclude(user__role="voice artist")
            else:
                # If user role is not recognized, return empty result
                media = media.filter(tag='video')

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

class UserReportView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        
        # Calculate the date range for each report
        today = timezone.now()

        # Daily Report (last 24 hours)
        daily_start_date = today - timedelta(days=1)
        daily_media = Media.objects.filter(user=user, uploaded_at__gte=daily_start_date)
        
        # Weekly Report (last 7 days)
        weekly_start_date = today - timedelta(weeks=1)
        weekly_media = Media.objects.filter(user=user, uploaded_at__gte=weekly_start_date)
        
        # Monthly Report (last 30 days)
        monthly_start_date = today - timedelta(weeks=4)
        monthly_media = Media.objects.filter(user=user, uploaded_at__gte=monthly_start_date)

        # Serialize the data for all three reports
        daily_serializer = MediaSerializer(daily_media, many=True)
        weekly_serializer = MediaSerializer(weekly_media, many=True)
        monthly_serializer = MediaSerializer(monthly_media, many=True)
        user_serializer = CustomUserSerializer(user)
        # Return all three reports in the response
        return Response({
            "user": user_serializer.data,
            "daily_report": {"count": daily_media.count(), "media": daily_serializer.data},
            "weekly_report": {"count": weekly_media.count(), "media": weekly_serializer.data},
            "monthly_report": {"count": monthly_media.count(), "media": monthly_serializer.data}
        }, status=status.HTTP_200_OK)


class FileUploadReportView(APIView):
    # def get(self, request):
    #     today = now().date()

    #     # 📅 Daily Reports (last 7 days)
    #     last_7_days = [today - timedelta(days=i) for i in range(7)]
    #     daily_data = {
    #         str(day): DailyReport.objects.filter(date=day).first().file_count
    #         if DailyReport.objects.filter(date=day).exists() else 0
    #         for day in reversed(last_7_days)
    #     }

    #     # 📈 Weekly Reports (last 6 weeks)
    #     weekly_reports = WeeklyReport.objects.order_by('-week')[:6]
    #     weekly_data = {report.week: report.file_count for report in reversed(weekly_reports)}

    #     # 📊 Monthly Reports (last 6 months)
    #     monthly_reports = MonthlyReport.objects.order_by('-month')[:6]
    #     monthly_data = {report.month: report.file_count for report in reversed(monthly_reports)}

    #     return Response({
    #         "daily": daily_data,
    #         "weekly": weekly_data,
    #         "monthly": monthly_data,
    #     }, status=status.HTTP_200_OK)

    #  def get(self, request):
    #     today = now().date()

    #     # 📅 Daily Reports (last 7 days)
    #     last_7_days = [today - timedelta(days=i) for i in range(7)]
    #     daily_data = {
    #         str(day): DailyReport.objects.filter(date=day).first().file_count
    #         if DailyReport.objects.filter(date=day).exists() else 0
    #         for day in reversed(last_7_days)
    #     }

    #     # 📈 Weekly Reports (last 6 weeks)
    #     weekly_reports = WeeklyReport.objects.order_by('-week')[:6]
    #     weekly_data = {report.week: report.file_count for report in reversed(weekly_reports)}

    #     # 📊 Monthly Reports (last 6 months)
    #     monthly_reports = MonthlyReport.objects.order_by('-month')[:6]
    #     monthly_data = {report.month: report.file_count for report in reversed(monthly_reports)}

    #     # 🏆 Total Teams, Files, and Videos
    #     total_teams = Team.objects.count()
    #     total_files = Media.objects.count()
    #     total_videos = Media.objects.filter(tag="video").count()

    #     # 🆕 Today's Newly Created Teams, Files, and Videos
    #     today_new_teams = Team.objects.filter(created_at=today).count()
    #     today_new_files = Media.objects.filter(uploaded_at__date=today).count()
    #     today_new_videos = Media.objects.filter(uploaded_at__date=today, tag="video").count()

    #     return Response({
    #         "daily": daily_data,
    #         "weekly": weekly_data,
    #         "monthly": monthly_data,
    #         "total_teams": total_teams,
    #         "total_files": total_files,
    #         "total_videos": total_videos,
    #         "today_new_teams": today_new_teams,
    #         "today_new_files": today_new_files,
    #         "today_new_videos": today_new_videos,
    #     }, status=status.HTTP_200_OK)
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

        # 🏆 Total Teams, Files, and Videos
        total_teams = Team.objects.count()
        total_files = Media.objects.count()
        total_videos = Media.objects.filter(tag="video").count()
        total_scripts = Media.objects.filter(tag="script").count()
        total_voices = Media.objects.filter(tag="voice").count()

        # 🆕 Today's Newly Created Teams, Files, and Videos
        today_new_teams = Team.objects.filter(created_at=today).count()
        today_new_files = Media.objects.filter(uploaded_at__date=today).count()
        today_new_videos = Media.objects.filter(uploaded_at__date=today, tag="video").count()
        today_new_scripts = Media.objects.filter(uploaded_at__date=today, tag="script").count()
        today_new_voices = Media.objects.filter(uploaded_at__date=today, tag="voice").count()

        # Calculate percentages
        total_media_count = total_files if total_files > 0 else 1  # Avoid division by zero
        video_percentage = (total_videos / total_media_count) * 100
        script_percentage = (total_scripts / total_media_count) * 100
        voice_percentage = (total_voices / total_media_count) * 100

        return Response({
            "daily": daily_data,
            "weekly": weekly_data,
            "monthly": monthly_data,
            "total_teams": total_teams,
            "total_files": total_files,
            "total_videos": total_videos,
            "total_scripts": total_scripts,
            "total_voices": total_voices,
            "today_new_teams": today_new_teams,
            "today_new_files": today_new_files,
            "today_new_videos": today_new_videos,
            "today_new_scripts": today_new_scripts,
            "today_new_voices": today_new_voices,
            "video_percentage": round(video_percentage, 2),
            "script_percentage": round(script_percentage, 2),
            "voice_percentage": round(voice_percentage, 2),
        }, status=status.HTTP_200_OK)




