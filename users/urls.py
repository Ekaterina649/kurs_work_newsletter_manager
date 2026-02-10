
from django.contrib.auth.views import LoginView, LogoutView
from users.apps import UsersConfig
from django.urls import path

from users.forms import UserLoginForm
from users.views import RegisterView, ProfileView, ProfileUpdateView, UserListView, ToggleUserActiveView, \
    ConfirmEmailView

app_name = UsersConfig.name

urlpatterns = [
    path('login/', LoginView.as_view(authentication_form=UserLoginForm), name='login'),
    path('logout/', LogoutView.as_view(next_page='users:login'), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('confirm/<uidb64>/<token>/', ConfirmEmailView.as_view(), name='confirm_email'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile_edit'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/toggle/<int:pk>/', ToggleUserActiveView.as_view(), name='toggle_user_active'),
]