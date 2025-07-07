from rest_framework import serializers
from .models import CustomUser
from team_managements.models import Team
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError


class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'Name' ,'Phone', 'Address', 'ProfilePicture','role','password']

    def create(self, validated_data):
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data['email'],
            Name=validated_data.get('Name', ''),
            Phone=validated_data.get('Phone', ''),
            Address=validated_data.get('Address', ''),
            role=validated_data.get('role'),  
            ProfilePicture=validated_data.get('ProfilePicture', ''),
        )
        user.set_password(validated_data['password'])   
        user.is_active = False     
        user.save()
        return user

class CustomUserSerializer(serializers.ModelSerializer):
    teams = serializers.SerializerMethodField()
    manager_of = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'Name', 'Phone', 'role',
            'teams', 'manager_of', 'Address', 'ProfilePicture','is_active'
        ]

    def get_teams(self, obj):
        return [
            {
                "id": team.id,
                "name": team.name
            }
            for team in obj.teams.all()
        ]

    def get_manager_of(self, obj):
        try:
            return {
                "id": obj.managed_team.id,
                "name": obj.managed_team.name
            } if obj.managed_team else None
        except Team.DoesNotExist:
            return None  
    
    
class UserRoleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['role', 'Name', 'Phone', 'Address','is_active']

    def validate(self, data):
        user = self.instance

        # একাধিক টিমে অ্যাসাইন প্রতিরোধ
        if data.get('team') and CustomUser.objects.filter(team=data['team'], id__ne=user.id).filter(id=user.id).exists():
            raise serializers.ValidationError("এই ইউজার ইতোমধ্যে অন্য টিমে আছে।")

              
        # Ensure that an admin can update is_active (if included)
        
        return data




class TeamMembershipSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        many=True,
        required=False
    )
    manager = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Team
        fields = ['id', 'name', 'users', 'manager']


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = self.context['request'].user
        
        # Check if the old password is correct
        if not user.check_password(data['old_password']):
            raise serializers.ValidationError("The old password is incorrect.")
        
        # Check if the new password matches the confirmation
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("The new passwords do not match.")
        
        # Validate the new password strength using Django's built-in password validation
        try:
            password_validation.validate_password(data['new_password'], user)
        except ValidationError as e:
            raise serializers.ValidationError({"new_password": e.messages})
        
        return data