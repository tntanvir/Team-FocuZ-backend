# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from django.utils.timezone import now
from datetime import timedelta
from .models import  Media, DailyReport, WeeklyReport, MonthlyReport
from .serializers import MediaSerializer
from rest_framework.exceptions import ValidationError


class MediaView(APIView):
    def get(self, request, pk=None):
        if pk:
            try:
                media = Media.objects.get(pk=pk)
                serializer = MediaSerializer(media)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Media.DoesNotExist:
                return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)

        # Simple pagination setup
        paginator = PageNumberPagination()
        paginator.page_size = 10 
        queryset = Media.objects.all().order_by('-uploaded_at')
        paginated_qs = paginator.paginate_queryset(queryset, request)
        serializer = MediaSerializer(paginated_qs, many=True)
        return paginator.get_paginated_response(serializer.data)


    # def post(self, request):
    #     serializer = MediaSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save(user=request.user)
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def post(self, request):
        user = request.user
        file_url = request.data.get('file')
        title = request.data.get('title')
        tag = request.data.get('tag')

        # Ensure all fields are provided and valid
        if not file_url or not title or not tag:
            return Response({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

        # Check the file extension based on role
        role = user.role
        if role == 'script writer' and not file_url.endswith('.txt'):
            return Response({"error": "Script Writers can only upload text files."}, status=status.HTTP_400_BAD_REQUEST)
        elif role == 'voice artist' and not file_url.endswith(('.mp3', '.wav', '.aac')):
            return Response({"error": "Voice Artists can only upload audio files."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the Media object and save
        media_payload = {
            'user': user.id,
            'title': title,
            'tag': tag,
            'file': file_url,
        }

        serializer = MediaSerializer(data=media_payload)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        data = Media.objects.get(pk=pk)
        serializer = MediaSerializer(data, request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, pk):
        data = Media.objects.get(pk=pk)
        if not data:
            return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)
        data.delete()
        return Response({"message": "File deleted successfully"}, status=status.HTTP_204_NO_CONTENT)






class FileUploadReportView(APIView):
    def get(self, request):
        today = now().date()

        # 📅 Daily Reports (last 7 days)
        last_7_days = [today - timedelta(days=i) for i in range(7)]
        daily_data = {
            str(day): DailyReport.objects.filter(date=day).first().file_count
            if DailyReport.objects.filter(date=day).exists() else 0
            for day in reversed(last_7_days)
        }

        # 📈 Weekly Reports (last 6 weeks)
        weekly_reports = WeeklyReport.objects.order_by('-week')[:6]
        weekly_data = {report.week: report.file_count for report in reversed(weekly_reports)}

        # 📊 Monthly Reports (last 6 months)
        monthly_reports = MonthlyReport.objects.order_by('-month')[:6]
        monthly_data = {report.month: report.file_count for report in reversed(monthly_reports)}

        return Response({
            "daily": daily_data,
            "weekly": weekly_data,
            "monthly": monthly_data,
        }, status=status.HTTP_200_OK)
