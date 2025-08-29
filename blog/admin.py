from django.contrib import admin
from django.contrib.auth.models import Group
from .models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_published', 'view_count', 'created_at']
    list_filter = ['is_published', 'created_at']
    search_fields = ['title', 'content']
    list_editable = ['is_published']
    readonly_fields = ['view_count', 'created_at']

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'content')
        }),
        ('Медиа', {
            'fields': ('preview',)
        }),
        ('Публикация', {
            'fields': ('is_published',)
        }),
        ('Статистика', {
            'fields': ('view_count', 'created_at'),
            'classes': ('collapse',)
        })
    )

    def has_module_permission(self, request):
        """Только контент-менеджеры могут видеть модуль блога в админке"""
        return request.user.has_perm('blog.can_manage_blog')

    def has_view_permission(self, request, obj=None):
        return request.user.has_perm('blog.can_manage_blog')

    def has_add_permission(self, request):
        return request.user.has_perm('blog.can_manage_blog')

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm('blog.can_edit_any_blog_post')

    def has_delete_permission(self, request, obj=None):
        return request.user.has_perm('blog.can_delete_any_blog_post')


# Дополнительная настройка для удобного управления группами в админке
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    filter_horizontal = ['permissions']


# Перерегистрируем модель Group с новым админом
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)