from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Media, DailyReport, WeeklyReport, MonthlyReport
from datetime import date
from django.utils.timezone import now

@receiver(post_save, sender=Media)
def update_reports(sender, instance, created, **kwargs):
    if not created:
        return

    today = now().date()

    # Daily Report
    daily, _ = DailyReport.objects.get_or_create(date=today)
    daily.file_count += 1
    daily.save()

    # Weekly Report
    iso_year, iso_week, _ = today.isocalendar()  
    week_label = f"{iso_year}-W{iso_week:02d}"
    weekly, _ = WeeklyReport.objects.get_or_create(week=week_label)
    weekly.file_count += 1
    weekly.save()

    # Monthly Report
    month_label = today.strftime("%Y-%m")  
    monthly, _ = MonthlyReport.objects.get_or_create(month=month_label)
    monthly.file_count += 1
    monthly.save()
