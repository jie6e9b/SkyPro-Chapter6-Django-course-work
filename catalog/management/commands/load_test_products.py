from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import transaction
from catalog.models import Category, Product


class Command(BaseCommand):
    help = 'Загружает данные из фикстур с дополнительной обработкой'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Очистить существующие данные перед загрузкой',
        )

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                if options['clear']:
                    self.stdout.write('🗑️  Очистка существующих данных...')
                    Product.objects.all().delete()
                    Category.objects.all().delete()
                    self.stdout.write('✅ Данные очищены')

                self.stdout.write('📦 Загрузка данных из фикстур...')
                
                # Вызываем стандартную команду loaddata
                call_command('loaddata', 'catalog/fixtures/catalog_data.json')
                
                self.stdout.write('✅ Фикстуры загружены')
                
                # Показываем статистику
                categories_count = Category.objects.count()
                products_count = Product.objects.count()
                
                self.stdout.write(f'📁 Категорий: {categories_count}')
                self.stdout.write(f'📦 Продуктов: {products_count}')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Ошибка: {str(e)}')
            )