from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ObjectDoesNotExist


class Command(BaseCommand):
    help = 'Создаёт или обновляет группу "Менеджеры" и назначает ей необходимые права'

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name='Менеджеры')

        required_permissions = [
            # Права на просмотр и управление клиентами
            'mailings.can_view_any_clients',
            'mailings.can_edit_any_clients',

            # Права на просмотр и управление сообщениями
            'mailings.can_view_any_messages',
            'mailings.can_edit_any_messages',

            # Права на просмотр, редактирование и удаление рассылок
            'mailings.can_view_any_mailings',
            'mailings.can_edit_any_mailings',
            'mailings.can_delete_any_mailings',

            # Право на блокировку пользователей (из модели auth.User)
            'auth.change_user',

        ]

        added = []
        not_found = []

        for codename in required_permissions:
            try:
                permission = Permission.objects.get(codename=codename)
                group.permissions.add(permission)
                added.append(permission.name)
            except ObjectDoesNotExist:
                not_found.append(codename)

        if created:
            self.stdout.write(self.style.SUCCESS('Группа "Менеджеры" успешно создана'))
        else:
            self.stdout.write(self.style.SUCCESS('Группа "Менеджеры" уже существует, права обновлены'))

        if added:
            self.stdout.write(self.style.SUCCESS(f'Добавлено прав: {len(added)}'))
            for perm in added:
                self.stdout.write(f'  - {perm}')

        if not_found:
            self.stdout.write(self.style.WARNING(f'Не найдено прав: {len(not_found)}'))
            for codename in not_found:
                self.stdout.write(self.style.WARNING(f'  - {codename}'))

