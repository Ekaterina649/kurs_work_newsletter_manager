from django.urls import path

from .views import (
    MessageListView,
    MessageCreateView,
    MessageUpdateView,
    MessageDeleteView,
    ClientListView,
    ClientCreateView,
    ClientUpdateView,
    ClientDeleteView,
    MailingListView,
    MailingCreateView,
    MailingUpdateView,
    MailingDeleteView,
    AttemptListView,
    MailingSendView,
    DisableMailingView,
)

app_name = "mailings"

urlpatterns = [
    # Сообщения
    path("messages/", MessageListView.as_view(), name="message_list"),
    path("messages/create/", MessageCreateView.as_view(), name="message_create"),
    path(
        "messages/<int:pk>/update/", MessageUpdateView.as_view(), name="message_update"
    ),
    path(
        "messages/<int:pk>/delete/", MessageDeleteView.as_view(), name="message_delete"
    ),
    # Клиенты
    path("clients/", ClientListView.as_view(), name="client_list"),
    path("clients/create/", ClientCreateView.as_view(), name="client_create"),
    path("clients/<int:pk>/update/", ClientUpdateView.as_view(), name="client_update"),
    path("clients/<int:pk>/delete/", ClientDeleteView.as_view(), name="client_delete"),
    # Рассылки
    path("", MailingListView.as_view(), name="mailing_list"),
    path("create/", MailingCreateView.as_view(), name="mailing_create"),
    path("<int:pk>/update/", MailingUpdateView.as_view(), name="mailing_update"),
    path("<int:pk>/delete/", MailingDeleteView.as_view(), name="mailing_delete"),
    path("<int:pk>/send/", MailingSendView.as_view(), name="mailing_send"),
    path("attempts/", AttemptListView.as_view(), name="attempt_list"),
    path("<int:pk>/disable/", DisableMailingView.as_view(), name="mailing_disable"),
]
