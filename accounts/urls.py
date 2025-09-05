from django.urls import path
from .views import profile_view, profile_completion_view, login_view, logout_view, register_view

app_name = 'accounts'
urlpatterns = [
    path('profile/', profile_view, name='profile'),
    path('profile-completion/', profile_completion_view, name='profile-completion'),
    path('login/' ,login_view, name='login'),
    path('logout/' ,logout_view, name='logout'),
    path('register/' ,register_view, name='register'),
]