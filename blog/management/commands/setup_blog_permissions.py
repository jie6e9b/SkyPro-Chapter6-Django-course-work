from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from blog.models import BlogPost


class Command(BaseCommand):
    help = 'Создает группу "Контент-менеджер" и настраивает разрешения для блога'

    def handle(self, *args, **options):
        # Создаем или получаем группу "Контент-менеджер"
        content_manager_group, created = Group.objects.get_or_create(
            name='Контент-менеджер'
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS('Группа "Контент-менеджер" создана')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Группа "Контент-менеджер" уже существует')
            )

        # Получаем ContentType для модели BlogPost
        blog_post_ct = ContentType.objects.get_for_model(BlogPost)

        # Определяем разрешения для контент-менеджера
        blog_permissions = [
            'add_blogpost',
            'change_blogpost',
            'delete_blogpost',
            'view_blogpost',
            'can_manage_blog',
            'can_publish_blog_post',
            'can_edit_any_blog_post',
            'can_delete_any_blog_post',
        ]

        # Добавляем разрешения в группу
        for perm_codename in blog_permissions:
            try:
                permission = Permission.objects.get(
                    codename=perm_codename,
                    content_type=blog_post_ct
                )
                content_manager_group.permissions.add(permission)
                self.stdout.write(
                    self.style.SUCCESS(f'Разрешение {perm_codename} добавлено')
                )
            except Permission.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Разрешение {perm_codename} не найдено')
                )

        self.stdout.write(
            self.style.SUCCESS(
                'Настройка разрешений для группы "Контент-менеджер" завершена'
            )
        )
