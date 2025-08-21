from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.utils.html import format_html

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Кастомная админка для пользователей"""

    # Отображение в списке пользователей
    list_display = [
        'username',
        'email',
        'phone_number',
        'is_active',
        'is_staff',
        'date_joined',
        'avatar_preview'
    ]

    list_filter = [
        'is_staff',
        'is_superuser',
        'is_active',
        'date_joined'
    ]

    search_fields = [
        'username',
        'email',
        'phone_number',
        'first_name',
        'last_name'
    ]

    ordering = ['-date_joined']

    # Поля для редактирования существующего пользователя
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('phone_number', 'date_of_birth', 'avatar'),
            'classes': ('wide',),
        }),
    )

    # Поля для создания нового пользователя
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('email', 'phone_number'),
            'classes': ('wide',),
        }),
    )

    def avatar_preview(self, obj):
        """Превью аватара в списке пользователей"""
        if obj.avatar:
            return format_html(
                '<img src="{}" width="30" height="30" style="border-radius: 50%;" />',
                obj.avatar.url
            )
        return "Нет аватара"

    avatar_preview.short_description = 'Аватар'

    def get_readonly_fields(self, request, obj=None):
        """Делаем некоторые поля только для чтения для обычных админов"""
        readonly_fields = list(super().get_readonly_fields(request, obj))

        # Если это не суперпользователь, ограничиваем права
        if not request.user.is_superuser:
            readonly_fields.extend(['is_superuser', 'user_permissions', 'groups'])

        return readonly_fields