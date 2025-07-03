# urls.py
from django.urls import path
from .views import MediaView,FileUploadReportView

urlpatterns = [
    path('data/', MediaView.as_view(), name='media-data'),
    path('data/<int:pk>/', MediaView.as_view(), name='media-detail'),
    path('report/', FileUploadReportView.as_view(), name='file-report'),
]
