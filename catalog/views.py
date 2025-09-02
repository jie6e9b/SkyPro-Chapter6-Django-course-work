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
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache
from catalog.services import CategoryService

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
    """Главная страница каталога с пагинацией и фильтром неопубликованных товаров"""

    model = Product
    template_name = 'catalog/home.html'
    context_object_name = 'products'
    paginate_by = 6
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        show_unpublished = self.request.GET.get('show_unpublished', 'false').lower() == 'true'

        # Уникальный ключ кэша учитывает пользователя и фильтр
        cache_key = f"index_queryset_{user.id if user.is_authenticated else 'anon'}_{show_unpublished}"
        queryset = cache.get(cache_key)

        if not queryset:
            queryset = Product.objects.select_related('category')

            if show_unpublished:
                if user.is_authenticated:
                    if user.has_perm('catalog.can_unpublish_product'):
                        # Модератор видит все неопубликованные товары
                        queryset = queryset.filter(publish__in=['pending','rejected','unpublished'])
                    else:
                        # Обычные пользователи видят свои неопубликованные + опубликованные
                        queryset = queryset.filter(publish='published') | queryset.filter(owner=user).exclude(publish='published')
                else:
                    # Гости видят только опубликованные
                    queryset = queryset.filter(publish='published')
            else:
                # Фильтр выключен — показываем только опубликованные
                queryset = queryset.filter(publish='published')

            queryset = queryset.order_by('-created_at')
            cache.set(cache_key, queryset, 60 * 15)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        show_unpublished = self.request.GET.get('show_unpublished', 'false').lower() == 'true'

        context.update({
            'title': 'Главная страница - Skystore',
            'description': 'Добро пожаловать в наш каталог товаров!',
            'show_unpublished': show_unpublished,
            'can_view_unpublished': user.has_perm('catalog.can_unpublish_product'),
            'can_view_own_unpublished': user.is_authenticated,
        })

        # Количество неопубликованных товаров для текущего пользователя
        if user.is_authenticated:
            context['user_unpublished_count'] = Product.objects.filter(owner=user).exclude(publish='published').count()
        else:
            context['user_unpublished_count'] = 0

        return context


@method_decorator(cache_page(60 * 15), name='dispatch')
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

        # Добавляем информацию о правах пользователя
        user = self.request.user
        context['can_view_unpublished'] = user.has_perm('catalog.can_unpublish_product')
        context['is_owner'] = user.is_authenticated and product.owner == user
        context['is_moderator'] = user.has_perm('catalog.can_unpublish_product')
        context['can_edit'] = user.is_authenticated and product.owner == user
        context['can_delete'] = (user.is_authenticated and product.owner == user) or user.has_perm(
            'catalog.can_unpublish_product')

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

    def get_form_kwargs(self):
        """Передаем пользователя в форму"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

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
    """Class-based view для редактирования товара с использованием формы. Только владелец может редактировать."""

    model = Product
    form_class = ProductForm
    template_name = 'catalog/add_product.html'
    pk_url_kwarg = 'product_id'

    def get_form_kwargs(self):
        """Передаем пользователя в форму"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

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


@method_decorator(cache_page(60 * 5), name='dispatch')  # кэшируем на 5 минут
class CategoryProductsView(ListView):
    template_name = "catalog/category_products.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        user = self.request.user
        show_unpublished = self.request.GET.get('show_unpublished', 'false').lower() == 'true'

        # Уникальный ключ кэша для пользователя, категории и фильтра
        cache_key = f"category_{category_id}_products_{user.id if user.is_authenticated else 'anon'}_{show_unpublished}"
        queryset = cache.get(cache_key)

        if not queryset:
            queryset = Product.objects.filter(category_id=category_id).select_related('category')

            if show_unpublished:
                if user.is_authenticated:
                    if user.has_perm('catalog.can_unpublish_product'):
                        # Модератор видит все неопубликованные товары
                        queryset = queryset.filter(publish__in=['pending','rejected','unpublished'])
                    else:
                        # Обычные пользователи видят свои неопубликованные + опубликованные
                        queryset = queryset.filter(publish='published') | queryset.filter(owner=user).exclude(publish='published')
                else:
                    # Гости видят только опубликованные
                    queryset = queryset.filter(publish='published')
            else:
                # Фильтр выключен — показываем только опубликованные
                queryset = queryset.filter(publish='published')

            queryset = queryset.order_by('-created_at')
            cache.set(cache_key, queryset, 60 * 5)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_id = self.kwargs['category_id']
        category = Category.objects.get(id=category_id)
        context['category'] = category

        user = self.request.user
        show_unpublished = self.request.GET.get('show_unpublished', 'false').lower() == 'true'
        context['show_unpublished'] = show_unpublished
        context['can_view_unpublished'] = user.has_perm('catalog.can_unpublish_product')

        return context