from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import BlogPost
from .mixins import (
    ContentManagerRequiredMixin,
    BlogPublishRequiredMixin,
    BlogEditAnyRequiredMixin,
    BlogDeleteAnyRequiredMixin
)


class BlogPostListView(ListView):
    """Представление для отображения списка записей блога"""
    model = BlogPost
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 6
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()

        # Обычные пользователи видят только опубликованные записи
        if not self.request.user.has_perm('blog.can_manage_blog'):
            queryset = queryset.filter(is_published=True)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Блог - Skystore'
        context['can_manage_blog'] = self.request.user.has_perm('blog.can_manage_blog')
        return context


class BlogPostDetailView(DetailView):
    """Представление для отображения детальной информации о записи блога"""
    model = BlogPost
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)

        # Увеличиваем счетчик просмотров
        obj.view_count += 1
        obj.save(update_fields=['view_count'])

        # Проверяем права доступа к неопубликованным записям
        if not obj.is_published and not self.request.user.has_perm('blog.can_manage_blog'):
            from django.http import Http404
            raise Http404("Запись блога не найдена")

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'{self.object.title} - Блог'
        context['can_manage_blog'] = self.request.user.has_perm('blog.can_manage_blog')
        context['can_edit'] = self.request.user.has_perm('blog.can_edit_any_blog_post')
        context['can_delete'] = self.request.user.has_perm('blog.can_delete_any_blog_post')
        context['can_publish'] = self.request.user.has_perm('blog.can_publish_blog_post')
        return context


class BlogPostCreateView(LoginRequiredMixin, ContentManagerRequiredMixin, CreateView):
    """Представление для создания новой записи блога"""
    model = BlogPost
    fields = ['title', 'content', 'preview', 'is_published']
    template_name = 'blog/post_form.html'
    success_url = reverse_lazy('blog:post_list')

    def form_valid(self, form):
        messages.success(
            self.request,
            f'Запись блога "{form.cleaned_data["title"]}" успешно создана!'
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Создать запись - Блог',
            'button_text': 'Создать запись',
            'form_title': 'Создание новой записи блога'
        })
        return context


class BlogPostUpdateView(LoginRequiredMixin, BlogEditAnyRequiredMixin, UpdateView):
    """Представление для редактирования записи блога"""
    model = BlogPost
    fields = ['title', 'content', 'preview', 'is_published']
    template_name = 'blog/post_form.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'post_id': self.object.pk})

    def form_valid(self, form):
        messages.success(
            self.request,
            f'Запись блога "{form.cleaned_data["title"]}" успешно обновлена!'
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': f'Редактировать {self.object.title} - Блог',
            'button_text': 'Сохранить изменения',
            'form_title': f'Редактирование записи "{self.object.title}"',
            'is_edit': True
        })
        return context


class BlogPostDeleteView(LoginRequiredMixin, BlogDeleteAnyRequiredMixin, DeleteView):
    """Представление для удаления записи блога"""
    model = BlogPost
    template_name = 'blog/post_confirm_delete.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'
    success_url = reverse_lazy('blog:post_list')

    def delete(self, request, *args, **kwargs):
        post_title = self.get_object().title
        messages.success(
            self.request,
            f'Запись блога "{post_title}" успешно удалена!'
        )
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Удалить {self.object.title} - Блог'
        return context


@require_POST
@permission_required('blog.can_publish_blog_post', raise_exception=True)
def toggle_blog_post_status(request, post_id):
    """AJAX-представление для изменения статуса публикации записи блога"""
    try:
        post = get_object_or_404(BlogPost, id=post_id)

        # Переключаем статус публикации
        post.is_published = not post.is_published
        post.save()

        status_text = 'опубликована' if post.is_published else 'снята с публикации'

        return JsonResponse({
            'success': True,
            'is_published': post.is_published,
            'message': f'Запись "{post.title}" {status_text}'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Ошибка: {str(e)}'
        })