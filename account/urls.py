from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterUserView.as_view(), name='register'),
    path('login/', views.LoginUserView.as_view(), name='login'),
    path('logout/',views.LogoutUserView.as_view()),
    path('profile/',views.UserProfileView.as_view()),
    path('alluser/',views.AllUsersView.as_view()),
    path('alluser/<int:user_id>/',views.AllUsersView.as_view()),
]