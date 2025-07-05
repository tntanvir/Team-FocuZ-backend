

from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/',include('account.urls')),
    path('media/',include('media.urls')),
    path('team/',include('team_managements.urls')),
    path('report/',include('reports.urls')),
]
