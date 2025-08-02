from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from .models import Product, ContactInfo
import re


def index(request: HttpRequest) -> HttpResponse:
    """ Контроллер для отображения домашней страницы каталога"""
    
    # Получаем последние 5 созданных продуктов
    latest_products = Product.objects.select_related('category').order_by('-created_at')[:5]
    
    # Выводим информацию о последних продуктах в консоль
    print("=" * 50)
    print("🔥 ПОСЛЕДНИЕ 5 СОЗДАННЫХ ПРОДУКТОВ:")
    print("=" * 50)
    
    for i, product in enumerate(latest_products, 1):
        print(f"{i}. {product.name}")
        print(f"   Категория: {product.category.name}")
        print(f"   Цена: {product.price} руб.")
        print(f"   Создан: {product.created_at.strftime('%d.%m.%Y %H:%M')}")
        print(f"   Описание: {product.description[:100]}{'...' if len(product.description) > 100 else ''}")
        print("-" * 30)
    
    if not latest_products:
        print("❌ Продукты в базе данных не найдены")
    
    print("=" * 50)

    context = {
        'title': 'Главная страница - Skystore',
        'description': 'Добро пожаловать в наш каталог товаров!',
        'latest_products': latest_products,  # Передаем продукты в шаблон
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