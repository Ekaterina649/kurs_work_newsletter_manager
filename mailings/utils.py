from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Mailing, Attempt

def send_mailing(mailing: Mailing):
    """
    Отправка рассылки и создание Attempt для каждого получателя.
    """
    now = timezone.now()

    # Проверяем, активна ли рассылка
    if not (mailing.start_time <= now <= mailing.end_time):
        return f"Рассылка {mailing.id} не активна в данный момент."

    recipients = mailing.recipients.all()
    subject = mailing.message.subject
    message_text = mailing.message.body

    for recipient in recipients:
        try:
            send_mail(
                subject=subject,
                message=message_text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                fail_silently=False,
            )
            # создаём попытку со статусом 'Успешно'
            Attempt.objects.create(
                mailing=mailing,
                status='Успешно',
                server_response=f"Письмо отправлено: {recipient.email}"
            )
        except Exception as e:
            # создаём попытку со статусом 'Не успешно'
            Attempt.objects.create(
                mailing=mailing,
                status='Не успешно',
                server_response=str(e)
            )
    return f"Рассылка {mailing.id} завершена."
