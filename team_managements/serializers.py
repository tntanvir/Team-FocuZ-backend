from rest_framework import serializers
from .models import Team
from account.serializers import CustomUserSerializer
from account.models import CustomUser
class TeamSerializer(serializers.ModelSerializer):
    users = CustomUserSerializer(many=True, read_only=True)
    manager = CustomUserSerializer(read_only=True)

    class Meta:
        model = Team
        fields = ['id', 'name', 'users', 'manager', 'description', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        team = Team.objects.create(**validated_data)
        return team

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance