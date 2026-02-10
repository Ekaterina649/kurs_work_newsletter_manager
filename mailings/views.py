from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
    DetailView,
)

from mailings.forms import MailingForm, ClientForm, MessageForm
from mailings.models import Message, Client, Mailing, Attempt
from mailings.utils import send_mailing


class ManagerReadonlyMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.groups.filter(name="Менеджеры").exists():
            raise PermissionDenied("Менеджер имеет доступ только на просмотр")
        return super().dispatch(request, *args, **kwargs)


class ManagerContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_manager"] = self.request.user.groups.filter(
            name="Менеджеры"
        ).exists()
        return context


# @method_decorator(cache_page(60 * 5), name='dispatch')
class MessageListView(ManagerContextMixin, LoginRequiredMixin, ListView):
    model = Message
    template_name = "mailings/message_list.html"
    context_object_name = "messages"

    def get_queryset(self):
        if self.request.user.groups.filter(name="Менеджеры").exists():
            return Message.objects.all()
        return Message.objects.filter(owner=self.request.user)


class MessageCreateView(ManagerReadonlyMixin, LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("mailings:message_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(ManagerReadonlyMixin, LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("mailings:message_list")

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        return super().form_valid(form)


class MessageDeleteView(ManagerReadonlyMixin, LoginRequiredMixin, DeleteView):
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
        if self.request.user.groups.filter(name="Менеджеры").exists():
            return Client.objects.all()
        return Client.objects.filter(owner=self.request.user)


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy("mailings:client_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientUpdateView(ManagerReadonlyMixin, LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy("mailings:client_list")

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        return super().form_valid(form)


class ClientDeleteView(ManagerReadonlyMixin, LoginRequiredMixin, DeleteView):
    model = Client
    template_name = "mailings/post_confirm_delete.html"
    success_url = reverse_lazy("mailings:client_list")

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)


# @method_decorator(cache_page(60 * 5), name='dispatch')
class MailingListView(ManagerContextMixin, LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "mailings/mailing_list.html"
    context_object_name = "mailings"

    def get_queryset(self):
        if self.request.user.groups.filter(name="Менеджеры").exists():
            return Mailing.objects.all().order_by("-start_time")
        return Mailing.objects.filter(owner=self.request.user).order_by("-start_time")


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("mailings:mailing_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user  #  передаём пользователя в форму
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(ManagerReadonlyMixin, LoginRequiredMixin, UpdateView):
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


class MailingDeleteView(ManagerReadonlyMixin, LoginRequiredMixin, DeleteView):
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
        if self.request.user.groups.filter(name="Менеджеры").exists():
            return Attempt.objects.all()
        # Обычный пользователь видит попытки только своих рассылок
        return Attempt.objects.filter(mailing__owner=self.request.user)


# @method_decorator(cache_page(60 * 5), name='dispatch')
class HomeView(ManagerContextMixin, LoginRequiredMixin, TemplateView):
    template_name = "mailings/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()

        if self.request.user.groups.filter(name="Менеджеры").exists():
            # Менеджер видит всё
            context["total_mailings"] = Mailing.objects.count()
            context["active_mailings"] = Mailing.objects.filter(
                start_time__lte=now, end_time__gte=now
            ).count()
            context["total_clients"] = Client.objects.count()
            context["successful_attempts"] = Attempt.objects.filter(
                status="Успешно"
            ).count()
            context["failed_attempts"] = Attempt.objects.filter(
                status="Не успешно"
            ).count()
        else:
            # Обычный пользователь видит только свои
            context["total_mailings"] = Mailing.objects.filter(
                owner=self.request.user
            ).count()
            context["active_mailings"] = Mailing.objects.filter(
                owner=self.request.user, start_time__lte=now, end_time__gte=now
            ).count()
            context["total_clients"] = Client.objects.filter(
                owner=self.request.user
            ).count()
            context["successful_attempts"] = Attempt.objects.filter(
                mailing__owner=self.request.user, status="Успешно"
            ).count()
            context["failed_attempts"] = Attempt.objects.filter(
                mailing__owner=self.request.user, status="Не успешно"
            ).count()

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
