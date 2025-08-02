from django.core.management.base import BaseCommand
from catalog.models import ContactInfo


class Command(BaseCommand):
    help = 'Загружает начальную контактную информацию'

    def handle(self, *args, **options):
        # Проверяем, есть ли уже активная контактная информация
        if ContactInfo.objects.filter(is_active=True).exists():
            self.stdout.write('ℹ️  Активная контактная информация уже существует')
            return

        # Создаем начальную контактную информацию
        contact_info = ContactInfo.objects.create(
            company_name="Skystore",
            address="г. Москва, ул. Инновационная, д. 42, офис 815",
            phone="+7 (495) 123-45-67",
            email="info@skystore.ru",
            working_hours="Пн-Пт: 9:00-18:00, Сб-Вс: 10:00-16:00",
            description="Skystore - ваш надежный партнер в мире цифровых решений. Мы предлагаем качественные плагины, компоненты и инструменты для разработчиков.",
            is_active=True
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Создана контактная информация: {contact_info.company_name}'
            )
        )