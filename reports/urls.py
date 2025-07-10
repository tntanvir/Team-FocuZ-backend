from django.urls import path
from . import views

urlpatterns = [    
    path('report/', views.TeamReportView.as_view() , name='report'),
    path('report/<int:team_id>/',  views.TeamReportViews.as_view(), name='team-report'),
    path('admin/report/', views.ReportAdminView.as_view(), name='admin-report'),
]