from django.contrib import admin
from .models import Media,DailyReport,WeeklyReport, MonthlyReport

# Register your models here.

@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('title',  'file','team', 'uploaded_at')

@admin.register(DailyReport)
class DailyReportAdmin(admin.ModelAdmin):
    list_display = ('date', 'file_count')  # Show these columns in admin
    ordering = ['-date']

@admin.register(WeeklyReport)
class WeeklyReportAdmin(admin.ModelAdmin):
    list_display = ('week', 'file_count')
    ordering = ['-week']

@admin.register(MonthlyReport)
class MonthlyReportAdmin(admin.ModelAdmin):
    list_display = ('month', 'file_count')
    ordering = ['-month']
