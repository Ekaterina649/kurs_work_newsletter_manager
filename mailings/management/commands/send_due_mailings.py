from django.core.management.base import BaseCommand
from django.utils import timezone
from mailings.models import Mailing
from mailings.utils import send_mailing
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Отправляет все активные рассылки, у которых пришло время'

    def handle(self, *args, **options):
        now = timezone.now()
        mailings = Mailing.objects.filter(
            start_time__lte=now,
            end_time__gte=now,
        )

        if not mailings.exists():
            self.stdout.write("Нет активных рассылок на данный момент")
            return

        for mailing in mailings:
            try:
                self.stdout.write(f"Отправляем рассылку: {mailing}")
                result = send_mailing(mailing)
                self.stdout.write(self.style.SUCCESS(result))
            except Exception as e:
                logger.error(f"Ошибка при отправке рассылки {mailing.id}: {e}")
                self.stdout.write(self.style.ERROR(f"Ошибка: {e}"))