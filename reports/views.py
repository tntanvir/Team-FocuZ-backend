from django.db.models import Count, Q
from rest_framework.views import APIView
from rest_framework.response import Response
# from .models import Team, Media
from team_managements.models import Team
from media.models import Media
from rest_framework import status









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