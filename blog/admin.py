from django.contrib import admin
from .models import BlogPost

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'is_published', 'view_count')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'content')
    readonly_fields = ('view_count', 'created_at')
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'content', 'preview')
        }),
        ('Публикация', {
            'fields': ('is_published',)
        }),
        ('Статистика', {
            'fields': ('view_count', 'created_at')
        }),
    )
