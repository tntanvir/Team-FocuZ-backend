from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)


urlpatterns = [
    path('register/', views.RegisterUserView.as_view(), name='register'),
    path('login/', views.LoginUserView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/',views.LogoutUserView.as_view()),
     path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('profile/',views.UserProfileView.as_view()),
    path('alluser/',views.AllUsersView.as_view()),
    path('alluser/<int:user_id>/',views.AllUsersView.as_view()),
    path('team/<int:team_id>/update/', views.TeamMembershipUpdateView.as_view(), name='team-update'),
]