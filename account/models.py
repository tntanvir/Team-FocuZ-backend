from django.contrib.auth.models import AbstractUser
from django.db import models
from team_managements.models import Team


# Create your models here.

class CustomUser(AbstractUser):
    Name = models.CharField(max_length=150, blank=True, null=True)
    Phone = models.CharField(max_length=15, blank=True, null=True)
    Address = models.CharField(max_length=255, blank=True, null=True)
    ProfilePicture = models.URLField(max_length=200, blank=True, null=True)
    role = models.CharField(max_length=50, choices=[('admin', 'Admin'),('manager', 'Manager'), ('video editor', 'Video Editor'),('script writer','Script Writer'),('voice artist','Voice Artist')], default='script writer',blank=True, null=True)
    team = models.CharField(max_length=300,blank=True, null=True)
    

   