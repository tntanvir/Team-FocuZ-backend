from django.db import models
from django.conf import settings
# Create your models here.
class Media(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='media_files',blank=True, null=True)
    title = models.CharField(max_length=255)
    file = models.URLField(max_length=1000 ,null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    tag = models.CharField(max_length=100,choices=[('video','Video'),('script','Script'),('voice','Voice')], null=True, blank=True)

    def __str__(self):
        return self.title

class DailyReport(models.Model):
    date = models.DateField(auto_now_add=True)
    file_count = models.PositiveIntegerField(default=0)


class WeeklyReport(models.Model):
    week = models.CharField(max_length=10, unique=True)  # e.g., "2025-W27"
    file_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Week: {self.week} | Files: {self.file_count}"

class MonthlyReport(models.Model):
    month = models.CharField(max_length=7, unique=True)  # e.g., "2025-07"
    file_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Month: {self.month} | Files: {self.file_count}"