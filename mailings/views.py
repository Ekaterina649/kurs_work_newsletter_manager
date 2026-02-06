from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from mailings.models import Message, Client, Mailing


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'mailings/message_list.html'
    context_object_name = 'messages'


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    fields = ('subject', 'body')
    success_url = reverse_lazy('mailings:message_list')

class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    fields = ('subject', 'body')
    success_url = reverse_lazy('mailings:message_list')

class MessageDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Message
    template_name = 'mailings/post_confirm_delete.html'
    success_url = reverse_lazy('mailings:message_list')
    permission_required = 'mailings.delete_message'



class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'mailings/client_list.html'
    context_object_name = 'clients'


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    fields = "__all__"
    success_url = reverse_lazy('mailings:client_list')

class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    fields = "__all__"
    success_url = reverse_lazy('mailings:client_list')

class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = 'mailings/post_confirm_delete.html'
    success_url = reverse_lazy('mailings:client_list')


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailings/mailing_list.html'
    context_object_name = 'mailings'


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    fields = "__all__"
    success_url = reverse_lazy('mailings:mailing_list')

class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    fields = ('start_time', 'end_time', 'message', 'recipients')
    success_url = reverse_lazy('mailings:mailing_list')

class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = 'mailings/post_confirm_delete.html'
    success_url = reverse_lazy('mailings:mailing_list')
    permission_required = 'mailings.delete_message'