from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
    DetailView,
)

from mailings.forms import MailingForm, ClientForm, MessageForm
from mailings.mixins import (
    ManagerContextMixin,
    ManagerReadonlyMixin,
    InvalidateCacheMixin,
)
from mailings.models import Message, Client, Mailing, Attempt
from mailings.utils import send_mailing


class MessageListView(ManagerContextMixin, LoginRequiredMixin, ListView):
    model = Message
    template_name = "mailings/message_list.html"
    context_object_name = "messages"

    def get_queryset(self):
        user = self.request.user
        cache_key = f"messages_list_{user.id}"

        queryset = cache.get(cache_key)
        if queryset is None:
            if user.groups.filter(name="Менеджеры").exists():
                queryset = Message.objects.all()
            else:
                queryset = Message.objects.filter(owner=user)

            cache.set(cache_key, list(queryset), timeout=60 * 10)  # 10 минут

        return queryset if queryset is not None else Message.objects.none()


class MessageCreateView(
    ManagerReadonlyMixin, LoginRequiredMixin, InvalidateCacheMixin, CreateView
):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("mailings:message_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(
    ManagerReadonlyMixin, LoginRequiredMixin, InvalidateCacheMixin, UpdateView
):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("mailings:message_list")

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        return super().form_valid(form)


class MessageDeleteView(
    ManagerReadonlyMixin, LoginRequiredMixin, InvalidateCacheMixin, DeleteView
):
    model = Message
    template_name = "mailings/post_confirm_delete.html"
    success_url = reverse_lazy("mailings:message_list")

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


class ClientListView(ManagerContextMixin, LoginRequiredMixin, ListView):
    model = Client
    template_name = "mailings/client_list.html"
    context_object_name = "clients"

    def get_queryset(self):
        user = self.request.user
        cache_key = f"clients_list_{user.id}"

        queryset = cache.get(cache_key)
        if queryset is None:
            if user.groups.filter(name="Менеджеры").exists():
                queryset = Client.objects.all()
            else:
                queryset = Client.objects.filter(owner=user)
            cache.set(cache_key, list(queryset), timeout=60 * 10)

        return queryset if queryset is not None else Client.objects.none()


class ClientCreateView(LoginRequiredMixin, InvalidateCacheMixin, CreateView):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy("mailings:client_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientUpdateView(
    ManagerReadonlyMixin, LoginRequiredMixin, InvalidateCacheMixin, UpdateView
):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy("mailings:client_list")

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        return super().form_valid(form)


class ClientDeleteView(
    ManagerReadonlyMixin, LoginRequiredMixin, InvalidateCacheMixin, DeleteView
):
    model = Client
    template_name = "mailings/post_confirm_delete.html"
    success_url = reverse_lazy("mailings:client_list")

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)


class MailingListView(ManagerContextMixin, LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "mailings/mailing_list.html"
    context_object_name = "mailings"

    def get_queryset(self):
        user = self.request.user
        cache_key = f"mailings_list_{user.id}"

        queryset = cache.get(cache_key)
        if queryset is None:
            if user.groups.filter(name="Менеджеры").exists():
                queryset = Mailing.objects.all().order_by("-start_time")
            else:
                queryset = Mailing.objects.filter(owner=user).order_by("-start_time")
            cache.set(cache_key, list(queryset), timeout=60 * 10)

        return queryset if queryset is not None else Mailing.objects.none()


class MailingCreateView(LoginRequiredMixin, InvalidateCacheMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("mailings:mailing_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        #  передаём пользователя в форму
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(
    ManagerReadonlyMixin, LoginRequiredMixin, InvalidateCacheMixin, UpdateView
):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("mailings:mailing_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        return super().form_valid(form)


class MailingDeleteView(
    ManagerReadonlyMixin, LoginRequiredMixin, InvalidateCacheMixin, DeleteView
):
    model = Mailing
    template_name = "mailings/post_confirm_delete.html"
    success_url = reverse_lazy("mailings:mailing_list")

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)


class AttemptListView(ManagerContextMixin, LoginRequiredMixin, ListView):
    model = Attempt
    template_name = "mailings/attempt_list.html"
    context_object_name = "attempts"

    def get_queryset(self):
        user = self.request.user
        cache_key = f"attempts_list_{user.id}"

        queryset = cache.get(cache_key)
        if queryset is None:
            if user.groups.filter(name="Менеджеры").exists():
                queryset = Attempt.objects.all()
            else:
                queryset = Attempt.objects.filter(mailing__owner=user)
            cache.set(cache_key, list(queryset), timeout=60 * 5)

        return queryset if queryset is not None else Attempt.objects.none()


@method_decorator(cache_page(60 * 5), name="dispatch")  # можно оставить
class HomeView(ManagerContextMixin, LoginRequiredMixin, TemplateView):
    template_name = "mailings/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        cache_key = f"home_stats_{user.id}"

        data = cache.get(cache_key)
        if data is None:
            now = timezone.now()

            if user.groups.filter(name="Менеджеры").exists():
                data = {
                    "total_mailings": Mailing.objects.count(),
                    "active_mailings": Mailing.objects.filter(
                        start_time__lte=now, end_time__gte=now
                    ).count(),
                    "total_clients": Client.objects.count(),
                    "successful_attempts": Attempt.objects.filter(
                        status="Успешно"
                    ).count(),
                    "failed_attempts": Attempt.objects.filter(
                        status="Не успешно"
                    ).count(),
                }
            else:
                data = {
                    "total_mailings": Mailing.objects.filter(owner=user).count(),
                    "active_mailings": Mailing.objects.filter(
                        owner=user, start_time__lte=now, end_time__gte=now
                    ).count(),
                    "total_clients": Client.objects.filter(owner=user).count(),
                    "successful_attempts": Attempt.objects.filter(
                        mailing__owner=user, status="Успешно"
                    ).count(),
                    "failed_attempts": Attempt.objects.filter(
                        mailing__owner=user, status="Не успешно"
                    ).count(),
                }

            cache.set(cache_key, data, timeout=60 * 5)

        context.update(data)
        return context


class MailingSendView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = "mailings/mailing_send_confirm.html"  # новый шаблон

    def dispatch(self, request, *args, **kwargs):
        mailing = self.get_object()
        # Проверка прав: только владелец может запускать
        if mailing.owner != request.user:
            raise PermissionDenied("Только владелец может отправлять рассылку")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        mailing = self.get_object()
        # Отправляем рассылку
        result = send_mailing(mailing)
        # Показываем страницу подтверждения с информацией
        return render(
            request, self.template_name, {"mailing": mailing, "result": result}
        )


class DisableMailingView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if not request.user.groups.filter(name="Менеджеры").exists():
            raise PermissionDenied("У вас нет доступа")

        mailing = get_object_or_404(Mailing, pk=pk)
        # Отключаем рассылку
        mailing.is_disabled = True
        mailing.save()
        return redirect("mailings:mailing_list")
