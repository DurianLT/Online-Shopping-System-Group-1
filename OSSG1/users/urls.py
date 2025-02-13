from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views
from .views import CustomLoginView, RegisterView,UserProfileView,PasswordResetByUsernameView,UserProfileUpdateView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('password_reset/', PasswordResetByUsernameView.as_view(), name='password_reset_by_username'),
    path('profile/edit/', UserProfileUpdateView.as_view(), name='edit_profile'),
]