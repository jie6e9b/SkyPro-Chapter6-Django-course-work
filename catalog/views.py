from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.decorators import permission_required
from django.views.decorators.http import require_POST
from .models import Product, ContactInfo, Category
from .forms import ProductForm
import re


class OwnerOrModeratorRequiredMixin(UserPassesTestMixin):
    """
    Миксин для проверки, что пользователь является владельцем продукта или модератором.
    Модератор определяется наличием права 'catalog.can_unpublish_product'.
    """
    
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
            
        # Получаем продукт
        product = get_object_or_404(Product, pk=self.kwargs.get('product_id'))
        
        # Проверяем, является ли пользователь владельцем
        is_owner = product.owner == self.request.user
        
        # Проверяем, является ли пользователь модератором
        is_moderator = self.request.user.has_perm('catalog.can_unpublish_product')
        
        return is_owner or is_moderator

    def handle_no_permission(self):
        """Переопределяем обработку отказа в доступе"""
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()  # Перенаправит на логин
        else:
            raise PermissionDenied("У вас нет прав для выполнения этого действия.")


class OwnerRequiredMixin(UserPassesTestMixin):
    """
    Миксин для проверки, что пользователь является владельцем продукта.
    Только для редактирования.
    """
    
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
            
        # Получаем продукт
        product = get_object_or_404(Product, pk=self.kwargs.get('product_id'))
        
        # Проверяем, является ли пользователь владельцем
        return product.owner == self.request.user

    def handle_no_permission(self):
        """Переопределяем обработку отказа в доступе"""
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()  # Перенаправит на логин
        else:
            raise PermissionDenied("Только владелец может редактировать этот товар.")


class IndexView(ListView):
    """Class-based view для отображения домашней страницы каталога с пагинацией"""
    
    model = Product
    template_name = 'catalog/home.html'
    context_object_name = 'products'
    paginate_by = 6
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Product.objects.select_related('category')
        
        # Проверяем фильтр для неопубликованных товаров
        show_unpublished = self.request.GET.get('show_unpublished', 'false').lower() == 'true'
        
        if show_unpublished and self.request.user.has_perm('catalog.can_unpublish_product'):
            # Показываем неопубликованные товары (все статусы кроме 'published')
            queryset = queryset.exclude(publish='published')
        else:
            # Показываем только опубликованные товары
            queryset = queryset.filter(publish='published')
            
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Главная страница - Skystore',
            'description': 'Добро пожаловать в наш каталог товаров!',
        })
        
        # Добавляем информацию о фильтре в контекст
        show_unpublished = self.request.GET.get('show_unpublished', 'false').lower() == 'true'
        context['show_unpublished'] = show_unpublished
        context['can_view_unpublished'] = self.request.user.has_perm('catalog.can_unpublish_product')
        
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
            category=product.category,
            publish='published'  # Показываем только опубликованные в похожих товарах
        ).exclude(
            id=product.pk
        ).order_by('-created_at')[:4]

        context['related_products'] = related_products
        
        # Добавляем информацию о правах на просмотр неопубликованных товаров
        context['can_view_unpublished'] = self.request.user.has_perm('catalog.can_unpublish_product')
        
        return context


@require_POST
@permission_required('catalog.can_unpublish_product', raise_exception=True)
def toggle_product_status(request, product_id):
    """AJAX-представление для изменения статуса публикации товара"""
    try:
        product = get_object_or_404(Product, id=product_id)
        
        new_status = request.POST.get('status')
        if new_status in ['published', 'unpublished', 'pending', 'rejected']:
            old_status_display = product.get_publish_display()
            product.publish = new_status
            product.save()
            
            new_status_display = product.get_publish_display()
            
            return JsonResponse({
                'success': True,
                'new_status': new_status,
                'new_status_display': new_status_display,
                'message': f'Статус товара "{product.name}" изменен с "{old_status_display}" на "{new_status_display}"'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Некорректный статус'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Ошибка: {str(e)}'
        })


class AddProductView(LoginRequiredMixin, CreateView):
    """Class-based view для добавления нового товара с использованием формы"""
    
    model = Product
    form_class = ProductForm
    template_name = 'catalog/add_product.html'
    success_url = reverse_lazy('catalog:index')
    
    def form_valid(self, form):
        """Автоматически привязываем продукт к текущему пользователю"""
        form.instance.owner = self.request.user
        messages.success(
            self.request, 
            f'Товар "{form.cleaned_data["name"]}" успешно добавлен!'
        )
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Добавить товар - Skystore',
            'button_text': 'Добавить товар',
            'cancel_url': reverse_lazy('catalog:index'),
            'form_title': 'Создание нового товара'
        })
        return context
    
    def form_invalid(self, form):
        messages.error(
            self.request, 
            'Пожалуйста, исправьте ошибки в форме.'
        )
        return super().form_invalid(form)


class EditProductView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
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


class DeleteProductView(LoginRequiredMixin, OwnerOrModeratorRequiredMixin, DeleteView):
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