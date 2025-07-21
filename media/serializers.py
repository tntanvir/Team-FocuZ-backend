from rest_framework import serializers
from .models import Media
from account.serializers import CustomUserSerializer
from team_managements.serializers import TeamSerializer
class MediaSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    team = TeamSerializer(read_only=True)
    class Meta:
        model = Media
        fields = ['id','user', 'title','team',  'file','tag','approved','download_count', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']  