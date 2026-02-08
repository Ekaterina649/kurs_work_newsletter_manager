from django.contrib.auth.views import LoginView, LogoutView

from users.apps import UsersConfig
from django.urls import path

from users.forms import UserLoginForm
from users.views import RegisterView, ProfileView, ProfileUpdateView

app_name = UsersConfig.name

urlpatterns = [path('login/',LoginView.as_view(authentication_form=UserLoginForm),name='login'),
            path('register/', RegisterView.as_view(), name='register'),
            path('logout/', LogoutView.as_view(next_page=''), name='logout'),
            path('profile/', ProfileView.as_view(), name='profile'),
            path('profile/edit/', ProfileUpdateView.as_view(), name='profile_edit'),
               ]