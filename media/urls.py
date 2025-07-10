# urls.py
from django.urls import path
from .views import MediaView,FileUploadReportView,UserReportView

urlpatterns = [
    path('data/', MediaView.as_view(), name='media-data'),
    path('data/<int:pk>/', MediaView.as_view(), name='media-detail'),
    path('report/', FileUploadReportView.as_view(), name='file-report'),
    path('user/report/', UserReportView.as_view(), name='daily-report'),
    
]
