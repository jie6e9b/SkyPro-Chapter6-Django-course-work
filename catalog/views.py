from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Product, ContactInfo, Category
import re


def index(request: HttpRequest) -> HttpResponse:
    """ Контроллер для отображения домашней страницы каталога с пагинацией"""

    # Получаем все продукты с сортировкой по дате создания (новые сначала)
    products_list = Product.objects.select_related('category').order_by('-created_at')

    # Настройки пагинации
    products_per_page = 6  # Количество товаров на странице
    paginator = Paginator(products_list, products_per_page)

    # Получаем номер страницы из GET-параметра
    page_number = request.GET.get('page', 1)

    try:
        products = paginator.page(page_number)
    except PageNotAnInteger:
        # Если номер страницы не является целым числом, показываем первую страницу
        products = paginator.page(1)
    except EmptyPage:
        # Если номер страницы больше общего количества страниц, показываем последнюю
        products = paginator.page(paginator.num_pages)

    # Выводим информацию о продуктах в консоль для отладки
    print("=" * 50)
    print(f"📦 КАТАЛОГ ТОВАРОВ (Страница {products.number} из {paginator.num_pages}):")
    print("=" * 50)
    print(f"Всего товаров: {paginator.count}")
    print(f"Товаров на странице: {len(products.object_list)}")
    print(f"Текущая страница: {products.number}")
    print(f"Есть следующая страница: {products.has_next()}")
    print(f"Есть предыдущая страница: {products.has_previous()}")

    for i, product in enumerate(products.object_list, 1):
        print(f"{i}. {product.name}")
        print(f"   Категория: {product.category.name}")
        print(f"   Цена: {product.price} руб.")
        print(f"   Создан: {product.created_at.strftime('%d.%m.%Y %H:%M')}")
        print("-" * 30)

    if not products.object_list:
        print("❌ Продукты в базе данных не найдены")

    print("=" * 50)

    context = {
        'title': 'Главная страница - Skystore',
        'description': 'Добро пожаловать в наш каталог товаров!',
        'products': products,  # Изменили с latest_products на products
        'paginator': paginator,  # Добавляем объект пагинатора
    }
    return render(request, 'catalog/home.html', context)


def contacts(request: HttpRequest) -> HttpResponse:
    """ Контроллер для отображения страницы контактов с формой обратной связи"""

    if request.method == 'POST':
        # Обработка данных формы обратной связи
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        message = request.POST.get('message', '').strip()

        # Валидация данных
        errors = []

        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            # Здесь можно добавить логику сохранения в БД или отправки email доработаем позднее

            messages.success(
                request,
                f'Спасибо, {name}! Ваше сообщение успешно отправлено. '
                f'Мы свяжемся с вами в ближайшее время.'
            )

            # Перенаправляем на ту же страницу, чтобы избежать повторной отправки при обновлении
            return redirect('contacts')

    # Получаем активную контактную информацию из базы данных
    try:
        contact_info = ContactInfo.objects.filter(is_active=True).first()
        if contact_info:
            context = {
                'title': 'Контакты - Skystore',
                'company_name': contact_info.company_name,
                'address': contact_info.address,
                'phone': contact_info.phone,
                'email': contact_info.email,
                'working_hours': contact_info.working_hours,
                'description': contact_info.description,
            }
        else:
            # Fallback данные, если в БД ничего нет
            context = {
                'title': 'Контакты - Skystore',
                'company_name': 'Skystore',
                'address': 'г. Москва, ул. Примерная, д. 123, офис 456',
                'phone': '+7 (495) 123-45-67',
                'email': 'info@skystore.ru',
                'working_hours': 'Пн-Пт: 9:00-18:00, Сб-Вс: 10:00-16:00',
                'description': 'Свяжитесь с нами для получения дополнительной информации.',
            }
    except Exception as e:
        print(f"Ошибка при получении контактной информации: {e}")
        # Используем стандартные данные в случае ошибки
        context = {
            'title': 'Контакты - Skystore',
            'company_name': 'Skystore',
            'address': 'г. Москва, ул. Примерная, д. 123, офис 456',
            'phone': '+7 (495) 123-45-67',
            'email': 'info@skystore.ru',
            'working_hours': 'Пн-Пт: 9:00-18:00, Сб-Вс: 10:00-16:00',
            'description': 'Свяжитесь с нами для получения дополнительной информации.',
        }

    return render(request, 'catalog/contacts.html', context)


def product_detail(request: HttpRequest, product_id: int) -> HttpResponse:
    """Контроллер для отображения детальной информации о товаре
    Args: request (HttpRequest): HTTP запрос
          product_id (int): ID товара для отображения
    Returns: HttpResponse: Страница с детальной информацией о товаре или 404 """

    # Безопасное получение товара с связанной категорией
    # get_object_or_404 автоматически вернет 404, если товар не найден
    product = get_object_or_404(
        Product.objects.select_related('category'),
        id=product_id
    )

    # Выводим информацию о товаре в консоль для отладки
    print("=" * 50)
    print("📦 ИНФОРМАЦИЯ О ТОВАРЕ:")
    print("=" * 50)
    print(f"ID: {product.pk}")
    print(f"Название: {product.name}")
    print(f"Категория: {product.category.name}")
    print(f"Цена: {product.price} руб.")
    print(f"Создан: {product.created_at.strftime('%d.%m.%Y %H:%M')}")
    print(f"Обновлен: {product.updated_at.strftime('%d.%m.%Y %H:%M')}")
    print(f"Описание: {product.description}")
    if product.image:
        print(f"Изображение: {product.image.url}")
    print("=" * 50)

    # Получаем связанные товары из той же категории (исключая текущий)
    related_products = Product.objects.filter(
        category=product.category
    ).exclude(
        id=product.pk
    ).order_by('-created_at')[:4]  # Берем 4 связанных товара

    context = {
        'title': f'{product.name} - Skystore',
        'product': product,
        'related_products': related_products,
    }

    return render(request, 'catalog/product_detail.html', context)


def add_product(request):
    """Контроллер для добавления нового товара"""
    if request.method == 'POST':
        # Получаем данные из формы
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        category_id = request.POST.get('category')
        image = request.FILES.get('image')

        # Простая валидация
        if name and description and price:
            # Создаем продукт
            product = Product.objects.create(
                name=name,
                description=description,
                price=price,
                category_id=category_id,
                image=image
            )
            messages.success(request, 'Товар успешно добавлен!')
            return redirect('index')
        else:
            messages.error(request, 'Заполните все обязательные поля!')

    categories = Category.objects.all()
    return render(request, 'catalog/add_product.html', {'categories': categories})