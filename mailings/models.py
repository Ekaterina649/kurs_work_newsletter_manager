from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from config import settings


class Client(models.Model):
    email = models.EmailField(
        unique=True, help_text="Укажите email", verbose_name="email"
    )
    full_name = models.CharField(
        max_length=100, help_text="Укажите полное имя", verbose_name="Полное имя"
    )
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Владелец",
        related_name="clients",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.email} - {self.full_name}"

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        permissions = [
            ("can_view_any_clients", "Может просматривать любых клиентов"),
            ("can_edit_any_clients", "Может редактировать любых клиентов"),
        ]


class Message(models.Model):
    subject = models.CharField(
        max_length=255, help_text="Укажите тему письма", verbose_name="Тема письма"
    )
    body = models.TextField(
        help_text="Укажите текст письма", verbose_name="текст письма"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Владелец",
        related_name="messages",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        permissions = [
            ("can_view_any_messages", "Может просматривать любые сообщения"),
            ("can_edit_any_messages", "Может редактировать любые сообщения"),
        ]


class Mailing(models.Model):
    start_time = models.DateTimeField(
        help_text="Укажите дату и время начала отправки",
        verbose_name="Дата и время начала отправки",
    )
    end_time = models.DateTimeField(
        help_text="Укажите дату и время окончания отправки",
        verbose_name="Дата и время окончания отправки",
    )
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, verbose_name="Сообщение письма"
    )
    recipients = models.ManyToManyField(
        Client, verbose_name="Список клиентов, которые получат данную рассылку"
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Владелец",
        related_name="mailings",
        null=True,
        blank=True,
    )
    is_disabled = models.BooleanField(default=False)

    def clean(self):
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError("Дата начала должна быть раньше даты окончания")

    @property
    def status(self):
        now = timezone.now()
        if now < self.start_time:
            return "Создана"
        elif self.start_time <= now <= self.end_time:
            return "Запущена"
        return "Завершена"

    def __str__(self):
        return f"Рассылка - {self.message}"

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        permissions = [
            ("can_view_any_mailings", "Может просматривать любые рассылки"),
            ("can_edit_any_mailings", "Может редактировать любые рассылки"),
            ("can_delete_any_mailings", "Может удалять любые рассылки"),
        ]


class Attempt(models.Model):

    STATUS_CHOICES = [
        ("Успешно", "Успешно"),
        ("Не успешно", "Не успешно"),
    ]

    attempt_time = models.DateTimeField(
        auto_now_add=True, verbose_name="дата и время попытки"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, verbose_name="статус попытки"
    )
    server_response = models.TextField(verbose_name="ответ почтового сервера")
    mailing = models.ForeignKey(
        Mailing, on_delete=models.CASCADE, verbose_name="рассылка"
    )

    def __str__(self):
        return f"Попытка рассылки - {self.status}"

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылок"
