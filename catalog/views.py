from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .models import Product, ContactInfo, Category
from .forms import ProductForm
import re


class IndexView(ListView):
    """Class-based view для отображения домашней страницы каталога с пагинацией"""
    
    model = Product
    template_name = 'catalog/home.html'
    context_object_name = 'products'
    paginate_by = 6
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Product.objects.select_related('category').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Главная страница - Skystore',
            'description': 'Добро пожаловать в наш каталог товаров!',
        })
        return context


class ProductDetailView(DetailView):
    """Class-based view для отображения детальной информации о товаре"""
    
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'
    pk_url_kwarg = 'product_id'

    def get_queryset(self):
        return Product.objects.select_related('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = context['product']

        context['title'] = f'{product.name} - Skystore'

        # Получаем связанные товары из той же категории (исключая текущий)
        related_products = Product.objects.filter(
            category=product.category
        ).exclude(
            id=product.pk
        ).order_by('-created_at')[:4]

        context['related_products'] = related_products
        return context


class AddProductView(LoginRequiredMixin, CreateView):
    """Class-based view для добавления нового товара с использованием формы"""
    
    model = Product
    form_class = ProductForm
    template_name = 'catalog/add_product.html'
    success_url = reverse_lazy('catalog:index')  # Исправлено
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Добавить товар - Skystore',
            'button_text': 'Добавить товар',
            'cancel_url': reverse_lazy('catalog:index'),  # Исправлено
            'form_title': 'Создание нового товара'
        })
        return context
    
    def form_valid(self, form):
        messages.success(
            self.request, 
            f'Товар "{form.cleaned_data["name"]}" успешно добавлен!'
        )
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(
            self.request, 
            'Пожалуйста, исправьте ошибки в форме.'
        )
        return super().form_invalid(form)


class EditProductView(LoginRequiredMixin, UpdateView):
    """Class-based view для редактирования товара с использованием формы"""
    
    model = Product
    form_class = ProductForm
    template_name = 'catalog/add_product.html'
    pk_url_kwarg = 'product_id'
    
    def get_success_url(self):
        return reverse_lazy('catalog:product_detail', kwargs={'product_id': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': f'Редактировать {self.object.name} - Skystore',
            'button_text': 'Сохранить изменения',
            'cancel_url': reverse_lazy('catalog:product_detail', kwargs={'product_id': self.object.pk}),
            'form_title': f'Редактирование товара "{self.object.name}"',
            'is_edit': True
        })
        return context
    
    def form_valid(self, form):
        messages.success(
            self.request, 
            f'Товар "{form.cleaned_data["name"]}" успешно обновлен!'
        )
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(
            self.request, 
            'Пожалуйста, исправьте ошибки в форме.'
        )
        return super().form_invalid(form)


class DeleteProductView(LoginRequiredMixin, DeleteView):
    """Class-based view для удаления товара"""
    
    model = Product
    template_name = 'catalog/delete_product.html'
    pk_url_kwarg = 'product_id'
    success_url = reverse_lazy('catalog:index')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': f'Удалить {self.object.name} - Skystore',
            'cancel_url': reverse_lazy('catalog:product_detail', kwargs={'product_id': self.object.pk})
        })
        return context
    
    def delete(self, request, *args, **kwargs):
        product_name = self.get_object().name
        messages.success(
            self.request, 
            f'Товар "{product_name}" успешно удален!'
        )
        return super().delete(request, *args, **kwargs)


class ContactsView(TemplateView):
    """Class-based view для отображения страницы контактов с формой обратной связи"""

    template_name = 'catalog/contacts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем активную контактную информацию из базы данных
        try:
            contact_info = ContactInfo.objects.filter(is_active=True).first()
            if contact_info:
                context.update({
                    'title': 'Контакты - Skystore',
                    'company_name': contact_info.company_name,
                    'address': contact_info.address,
                    'phone': contact_info.phone,
                    'email': contact_info.email,
                    'working_hours': contact_info.working_hours,
                    'description': contact_info.description,
                })
            else:
                # Fallback данные, если в БД ничего нет
                context.update({
                    'title': 'Контакты - Skystore',
                    'company_name': 'Skystore',
                    'address': 'г. Москва, ул. Примерная, д. 123, офис 456',
                    'phone': '+7 (495) 123-45-67',
                    'email': 'info@skystore.ru',
                    'working_hours': 'Пн-Пт: 9:00-18:00, Сб-Вс: 10:00-16:00',
                    'description': 'Свяжитесь с нами для получения дополнительной информации.',
                })
        except Exception as e:
            print(f"Ошибка при получении контактной информации: {e}")
            # Используем стандартные данные в случае ошибки
            context.update({
                'title': 'Контакты - Skystore',
                'company_name': 'Skystore',
                'address': 'г. Москва, ул. Примерная, д. 123, офис 456',
                'phone': '+7 (495) 123-45-67',
                'email': 'info@skystore.ru',
                'working_hours': 'Пн-Пт: 9:00-18:00, Сб-Вс: 10:00-16:00',
                'description': 'Свяжитесь с нами для получения дополнительной информации.',
            })

        return context

    def post(self, request, *args, **kwargs):
        """Обработка POST запроса для формы обратной связи"""
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        message = request.POST.get('message', '').strip()

        # Валидация данных
        errors = []

        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            messages.success(
                request,
                f'Спасибо, {name}! Ваше сообщение успешно отправлено. '
                f'Мы свяжемся с вами в ближайшее время.'
            )
            # Исправлено: добавлено пространство имен
            return redirect('catalog:contacts')

        return self.get(request, *args, **kwargs)