
from django.core.exceptions import PermissionDenied


from django.core.cache import cache


class InvalidateCacheMixin:
    """
    Инвалидирует кеш списков и главной страницы после создания/изменения/удаления.
    Используется для CreateView, UpdateView, DeleteView.
    """

    def get_cache_keys_to_invalidate(self):
        user = self.request.user
        return [
            f"messages_list_{user.id}",
            f"clients_list_{user.id}",
            f"mailings_list_{user.id}",
            f"attempts_list_{user.id}",
            f"home_stats_{user.id}",
        ]

    def form_valid(self, form):
        # Сначала выполняем сохранение
        response = super().form_valid(form)
        # Потом очищаем кеш
        self._invalidate_caches()
        return response

    def delete(self, request, *args, **kwargs):
        # Сначала выполняем удаление
        response = super().delete(request, *args, **kwargs)
        # Потом очищаем кеш
        self._invalidate_caches()
        return response

    def _invalidate_caches(self):
        """Внутренний метод для очистки всех ключей"""
        keys = self.get_cache_keys_to_invalidate()
        for key in keys:
            cache.delete(key)


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
