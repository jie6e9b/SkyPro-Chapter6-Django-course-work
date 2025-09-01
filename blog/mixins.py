from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class ContentManagerRequiredMixin(UserPassesTestMixin):
    """
    Миксин для проверки, что пользователь является контент-менеджером.
    Контент-менеджер определяется наличием права 'blog.can_manage_blog'.
    """

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False

        # Проверяем, является ли пользователь контент-менеджером
        return self.request.user.has_perm('blog.can_manage_blog')

    def handle_no_permission(self):
        """Переопределяем обработку отказа в доступе"""
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()  # Перенаправит на логин
        else:
            raise PermissionDenied(
                "У вас нет прав для управления блогом. "
                "Только контент-менеджеры могут выполнять это действие."
            )


class BlogPublishRequiredMixin(UserPassesTestMixin):
    """
    Миксин для проверки, что пользователь может публиковать записи блога.
    """

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False

        # Проверяем право на публикацию записей блога
        return self.request.user.has_perm('blog.can_publish_blog_post')

    def handle_no_permission(self):
        """Переопределяем обработку отказа в доступе"""
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        else:
            raise PermissionDenied(
                "У вас нет прав для публикации записей блога."
            )


class BlogEditAnyRequiredMixin(UserPassesTestMixin):
    """
    Миксин для проверки, что пользователь может редактировать любые записи блога.
    """

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False

        # Проверяем право на редактирование любых записей блога
        return self.request.user.has_perm('blog.can_edit_any_blog_post')

    def handle_no_permission(self):
        """Переопределяем обработку отказа в доступе"""
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        else:
            raise PermissionDenied(
                "У вас нет прав для редактирования записей блога."
            )


class BlogDeleteAnyRequiredMixin(UserPassesTestMixin):
    """
    Миксин для проверки, что пользователь может удалять любые записи блога.
    """

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False

        # Проверяем право на удаление любых записей блога
        return self.request.user.has_perm('blog.can_delete_any_blog_post')

    def handle_no_permission(self):
        """Переопределяем обработку отказа в доступе"""
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        else:
            raise PermissionDenied(
                "У вас нет прав для удаления записей блога."
            )