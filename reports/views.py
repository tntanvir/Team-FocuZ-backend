from django.db.models import Count, Q
from rest_framework.views import APIView
from rest_framework.response import Response
# from .models import Team, Media
from team_managements.models import Team
from media.models import Media
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from rest_framework.permissions import IsAuthenticated

class ReportAdminView(APIView):
    
    
    def get(self, request):
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        report = []

        for team in Team.objects.all():
            members = team.users.all()
            media_qs = Media.objects.filter(user__in=members)
            # appdata = Media.objects.filter(approved=True).count()
            # print(appdata)

            # Define a helper to filter by tag and time
            def get_counts(tag):
                tagged = media_qs.filter(tag=tag)
                return {
                    'daily': tagged.filter(uploaded_at__date=today).count(),
                    'weekly': tagged.filter(uploaded_at__date__gte=week_ago).count(),
                    'monthly': tagged.filter(uploaded_at__date__gte=month_ago).count(),
                    # 'approved': tagged.filter(approved=True).count()
                }

            video_stats = get_counts('video')
            script_stats = get_counts('script')
            voice_stats = get_counts('voice')

            report.append({
                'team_name': team.name,
                'video_editor': video_stats,
                'script_writer': script_stats,
                'voice_artist': voice_stats,
                # 'total_approved': appdata
            })

        return Response(report)
class ReportManager(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        report = []

        # Get the team for the current user
        user_team = Team.objects.filter(users=request.user).first()

        if not user_team:
            return Response({"error": "User is not part of any team"}, status=404)

        # Get the members of the user's team
        members = user_team.users.all()

        # Filter media based on the team's users
        media_qs = Media.objects.filter(user__in=members)

        # Define a helper function to get counts for each tag
        def get_counts(tag):
            tagged = media_qs.filter(tag=tag)
            return {
                'daily': tagged.filter(uploaded_at__date=today).count(),
                'weekly': tagged.filter(uploaded_at__date__gte=week_ago).count(),
                'monthly': tagged.filter(uploaded_at__date__gte=month_ago).count(),
            }

        # Get statistics for video, script, and voice
        video_stats = get_counts('video')
        script_stats = get_counts('script')
        voice_stats = get_counts('voice')

        # Append data for the team to the report
        report.append({
            'team_name': user_team.name,
            'video_editor': video_stats,
            'script_writer': script_stats,
            'voice_artist': voice_stats,
        })

        return Response(report)
    
 
    







class TeamReportView(APIView):
    def get(self, request):
        report = []

        for team in Team.objects.all():
            members = team.users.all()

            media_qs = Media.objects.filter(user__in=members)

            total_files = media_qs.count()
            video_count = media_qs.filter(tag='video').count()
            script_count = media_qs.filter(tag='script').count()
            voice_count = media_qs.filter(tag='voice').count()

            report.append({
                'team_name': team.name,
                'total_members': members.count(),
                'total_files': total_files,
                'video_count': video_count,
                'script_count': script_count,
                'voice_count': voice_count
            })

        return Response(report)

class TeamReportViews(APIView):
    def get(self, request, team_id):
        try:
            team = Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            return Response({"error": "Team not found"}, status=status.HTTP_404_NOT_FOUND)

        members = team.users.all()
        member_details = []

        for member in members:
            member_media = member.media_files.all()  # Using related_name from Media.user

            video_files = member_media.filter(tag='video')
            script_files = member_media.filter(tag='script')
            voice_files = member_media.filter(tag='voice')

            member_details.append({
                "id": member.id,
                "username": member.username,
                "name": member.Name,
                "email": member.email,
                "phone": member.Phone,
                "role": member.role,
                "profile_picture": member.ProfilePicture,
                "total_files": member_media.count(),
                "video_count": video_files.count(),
                "script_count": script_files.count(),
                "voice_count": voice_files.count(),

                "videos": [
                    {
                        "id": media.id,
                        "title": media.title,
                        "file_url": media.file,
                        "uploaded_at": media.uploaded_at.strftime("%Y-%m-%d %H:%M")
                    }
                    for media in video_files
                ],

                "scripts": [
                    {
                        "id": media.id,
                        "title": media.title,
                        "file_url": media.file,
                        "uploaded_at": media.uploaded_at.strftime("%Y-%m-%d %H:%M")
                    }
                    for media in script_files
                ],

                "voices": [
                    {
                        "id": media.id,
                        "title": media.title,
                        "file_url": media.file,
                        "uploaded_at": media.uploaded_at.strftime("%Y-%m-%d %H:%M")
                    }
                    for media in voice_files
                ]
            })

        team_media = Media.objects.filter(user__in=members)
        report = {
            "team_id": team.id,
            "team_name": team.name,
            "description": team.description,
            "total_members": members.count(),
            "total_files": team_media.count(),
            "video_count": team_media.filter(tag='video').count(),
            "script_count": team_media.filter(tag='script').count(),
            "voice_count": team_media.filter(tag='voice').count(),
            "members": member_details
        }

        return Response(report, status=status.HTTP_200_OK)