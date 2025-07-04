from rest_framework import serializers
from .models import CustomUser
from team_managements.models import Team



class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'Name' ,'Phone', 'Address', 'ProfilePicture','password']

    def create(self, validated_data):
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data['email'],
            Name=validated_data.get('Name', ''),
            Phone=validated_data.get('Phone', ''),
            Address=validated_data.get('Address', ''),
            ProfilePicture=validated_data.get('ProfilePicture', ''),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

# class CustomUserSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = CustomUser
#         fields = ['id','username', 'email', 'Name' ,'Phone','role', 'Address', 'ProfilePicture']

class CustomUserSerializer(serializers.ModelSerializer):
    teams = serializers.SerializerMethodField()
    manager_of = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'Name', 'Phone', 'role', 'teams', 'manager_of', 'Address', 'ProfilePicture']

    def get_teams(self, obj):
        return [team.name for team in obj.teams.all()]

    def get_manager_of(self, obj):
        return [team.name for team in obj.managed_teams.all()]
    

class UserRoleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['role', 'Name', 'Phone', 'Address']


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