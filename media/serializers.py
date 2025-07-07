from rest_framework import serializers
from .models import Media
from account.serializers import CustomUserSerializer

class MediaSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    class Meta:
        model = Media
        fields = ['id','user', 'title','team',  'file','tag', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']  