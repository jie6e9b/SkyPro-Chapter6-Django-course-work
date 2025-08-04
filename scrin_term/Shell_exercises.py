# ## 1. Создание категорий с помощью create():
#
# from catalog.models import Category, Product
#
# # Создание отдельных категорий
# category1 = Category.objects.create(name="Веб-разработка", description="Инструменты и плагины для веб-разработки")
# category2 = Category.objects.create(name="Мобильная разработка", description="Приложения и утилиты для мобильной разработки")
# category3 = Category.objects.create(name="Дизайн", description="Графические ресурсы и инструменты дизайна")
# category4 = Category.objects.create(name="DevOps",description="Инструменты для автоматизации и развертывания")
# print(f"Создано категорий: {Category.objects.count()}")
#
# ## 2. Создание продуктов с помощью create():
#
# # Получаем категории для связывания
# web_category = Category.objects.get(name="Веб-разработка")
# mobile_category = Category.objects.get(name="Мобильная разработка")
# design_category = Category.objects.get(name="Дизайн")
#
# # Создание продуктов
# product1 = Product.objects.create(name="Bootstrap Theme Pro", description="Профессиональная тема Bootstrap с адаптивным дизайном", price=2999.00, category=web_category)
# product2 = Product.objects.create(name="React Component Library", description="Библиотека готовых React компонентов", price=4500.00, category=web_category)
# product3 = Product.objects.create(name="Flutter UI Kit", description="Набор UI элементов для Flutter приложений", price=3200.00, category=mobile_category)
# product4 = Product.objects.create(name="Icon Pack Premium", description="Премиум набор из 500+ векторных иконок", price=1200.00, category=design_category)
# product5 = Product.objects.create(name="Django REST Template", description="Готовый шаблон для Django REST API", price=3800.00, category=web_category)
# print(f"Создано продуктов: {Product.objects.count()}")
#
# ## 3. Запрос на получение всех категорий:
#
# # Получить все категории
# all_categories = Category.objects.all()
# print("Все категории:")
# for category in all_categories:
#     print(f"ID: {category.id}, Название: {category.name}")
#
# ## 4. Запрос на получение всех продуктов:
# # Получить все продукты
# all_products = Product.objects.all()
# print("Все продукты:")
# for product in all_products:
#     print(f"ID: {product.id}, Название: {product.name}, Цена: {product.price}, Категория: {product.category.name}")
#
# ## 5. Запрос на получение продуктов определенной категории:
#
# web_category = Category.objects.get(name="Веб-разработка")
# web_products = Product.objects.filter(category=web_category)
# print("Продукты категории 'Веб-разработка':")
# for product in web_products:
#     print(f"- {product.name}: {product.price} руб.")
#
# ## 6. Запрос на обновление цены определенного продукта:
# product = Product.objects.get(name="Bootstrap Theme Pro")
# old_price = product.price
# product.price = 3500.00
# product.save()
#
# print(f"Цена '{product.name}' изменена с {old_price} на {product.price}")
#
# ## 7. Запрос на удаление продукта:
# product_to_delete = Product.objects.get(name="Icon Pack Premium")
# product_name = product_to_delete.name
# product_to_delete.delete()
# print(f"Продукт '{product_name}' удален")
#
