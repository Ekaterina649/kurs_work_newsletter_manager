from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from django.views.generic import CreateView, DetailView, UpdateView, ListView

from config import settings
from .forms import UserRegistrationForm, UserProfileForm
from .models import User


class RegisterView(CreateView):
    template_name = 'users/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.save()
        self.send_confirmation_email(user)
        messages.success(
            self.request,
            "Регистрация завершена! Проверьте почту и подтвердите email."
        )
        return redirect('users:login')

    def send_confirmation_email(self, user):
        from django.contrib.sites.shortcuts import get_current_site
        from django.template.loader import render_to_string

        current_site = get_current_site(self.request)
        protocol = 'https' if self.request.is_secure() else 'http'

        subject = 'Подтвердите ваш email'
        message = render_to_string('users/confirm_email.html', {
            'user': user,
            'domain': current_site.domain,
            'protocol': protocol,
            'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
        })

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )


class ConfirmEmailView(View):
    def get(self, request, uidb64, token):
        print("ConfirmEmailView вызван")
        print(f"uidb64: {uidb64}, token: {token}")

        try:
            uid = urlsafe_base64_decode(uidb64).decode('utf-8')
            user = User.objects.get(pk=uid)
            print(f"Пользователь: {user.email}, is_active: {user.is_active}")
        except Exception as e:
            print(f"Ошибка поиска: {e}")
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            print("Токен ВАЛИДНЫЙ → активируем")
            user.is_active = True
            user.save(update_fields=['is_active'])
            print(f"После сохранения is_active: {user.is_active}")

            login(request, user)
            messages.success(request, "Email подтверждён! Добро пожаловать!")
            return redirect('users:profile')
        else:
            print("Токен НЕ валидный")
            messages.error(request, "Ссылка недействительна или устарела. Попробуйте зарегистрироваться заново.")
            return redirect('users:login')

class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'users/profile.html'
    context_object_name = 'user'

    def get_object(self, queryset=None):
        return self.request.user


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user

class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'

    def test_func(self):
        return self.request.user.groups.filter(name='Менеджеры').exists()

class ToggleUserActiveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if not request.user.groups.filter(name='Менеджеры').exists():
            raise PermissionDenied("У вас нет доступа")

        user = get_object_or_404(User, pk=pk)
        # Не блокируем себя
        if user == request.user:
            raise PermissionDenied("Нельзя заблокировать себя")

        user.is_active = not user.is_active
        user.save()
        return redirect('users:user_list')