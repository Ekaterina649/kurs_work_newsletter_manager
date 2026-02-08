from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views.decorators.cache import cache_page
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, DetailView

from mailings.forms import MailingForm, ClientForm, MessageForm
from mailings.models import Message, Client, Mailing, Attempt
from mailings.utils import send_mailing

@method_decorator(cache_page(60 * 10), name='dispatch')
class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'mailings/message_list.html'
    context_object_name = 'messages'

    def get_queryset(self):
        if self.request.user.groups.filter(name='Менеджеры').exists():
            return Message.objects.all()
        return Message.objects.filter(owner=self.request.user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy('mailings:message_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy('mailings:message_list')

    def get_queryset(self):
        if self.request.user.groups.filter(name='Менеджеры').exists():
            return Message.objects.all()
        return Message.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        return super().form_valid(form)

class MessageDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Message
    template_name = 'mailings/post_confirm_delete.html'
    success_url = reverse_lazy('mailings:message_list')
    permission_required = 'mailings.delete_message'



class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'mailings/client_list.html'
    context_object_name = 'clients'

    def get_queryset(self):
        if self.request.user.groups.filter(name='Менеджеры').exists():
            return Client.objects.all()
        return Client.objects.filter(owner=self.request.user)


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy('mailings:client_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy('mailings:client_list')

    def get_queryset(self):
        if self.request.user.groups.filter(name='Менеджеры').exists():
            return Client.objects.all()
        return Client.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        return super().form_valid(form)

class ClientDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Client
    template_name = 'mailings/post_confirm_delete.html'
    success_url = reverse_lazy('mailings:client_list')
    permission_required = 'mailings.delete_client'

@method_decorator(cache_page(60 * 10), name='dispatch')
class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailings/mailing_list.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        if self.request.user.groups.filter(name='Менеджеры').exists():
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=self.request.user)


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy('mailings:mailing_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy('mailings:mailing_list')

    def get_queryset(self):
        if self.request.user.groups.filter(name='Менеджеры').exists():
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        return super().form_valid(form)

class MailingDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Mailing
    template_name = 'mailings/post_confirm_delete.html'
    success_url = reverse_lazy('mailings:mailing_list')
    permission_required = 'mailings.delete_mailing'

class AttemptListView(LoginRequiredMixin, ListView):
    model = Attempt
    template_name = 'mailings/attempt_list.html'
    context_object_name = 'attempts'

    def get_queryset(self):
        if self.request.user.groups.filter(name='Менеджеры').exists():
            return Attempt.objects.all()
        # Обычный пользователь видит попытки только своих рассылок
        return Attempt.objects.filter(mailing__owner=self.request.user)

@method_decorator(cache_page(60 * 5), name='dispatch')
class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'mailings/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()

        if self.request.user.groups.filter(name='Менеджеры').exists():
            # Менеджер видит всё
            context['total_mailings'] = Mailing.objects.count()
            context['active_mailings'] = Mailing.objects.filter(
                start_time__lte=now, end_time__gte=now
            ).count()
            context['total_clients'] = Client.objects.count()
            context['successful_attempts'] = Attempt.objects.filter(status='Успешно').count()
            context['failed_attempts'] = Attempt.objects.filter(status='Не успешно').count()
        else:
            # Обычный пользователь видит только свои
            context['total_mailings'] = Mailing.objects.filter(owner=self.request.user).count()
            context['active_mailings'] = Mailing.objects.filter(
                owner=self.request.user,
                start_time__lte=now, end_time__gte=now
            ).count()
            context['total_clients'] = Client.objects.filter(owner=self.request.user).count()
            context['successful_attempts'] = Attempt.objects.filter(
                mailing__owner=self.request.user, status='Успешно'
            ).count()
            context['failed_attempts'] = Attempt.objects.filter(
                mailing__owner=self.request.user, status='Не успешно'
            ).count()

        return context

class MailingSendView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = "mailings/mailing_send.html"

    def dispatch(self, request, *args, **kwargs):
        mailing = self.get_object()
        if mailing.owner != request.user and not request.user.groups.filter(name='Менеджеры').exists():
            raise PermissionDenied("У вас нет права отправлять эту рассылку")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        mailing = self.get_object()
        send_mailing(mailing)
        return redirect("mailings:mailing_list")