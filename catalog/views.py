from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
import re

def index(request: HttpRequest) -> HttpResponse:
    """ Контроллер для отображения домашней страницы каталога"""

    context = {
        'title': 'Главная страница - Skystore',
        'description': 'Добро пожаловать в наш каталог товаров!'
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

    # Контактная информация для отображения на странице
    context = {
        'title': 'Контакты - Skystore',
        'company_name': 'Skystore',
        'address': 'г. Москва, ул. Примерная, д. 123, офис 456',
        'phone': '+7 (495) 123-45-67',
        'email': 'info@skystore.ru',
        'working_hours': 'Пн-Пт: 9:00-18:00, Сб-Вс: 10:00-16:00'
    }
    return render(request, 'catalog/contacts.html', context)