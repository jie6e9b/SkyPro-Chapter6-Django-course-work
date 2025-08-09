from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import F
from .models import BlogPost


class BlogPostListView(ListView):
    model = BlogPost
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10


    def get_queryset(self):
        """Возвращаем только опубликованные статьи, отсортированные по дате создания"""
        return BlogPost.objects.filter(is_published=True).order_by('-created_at')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Блог'
        return context


class BlogPostDetailView(DetailView):
    model = BlogPost
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.title
        return context

    def get_object(self, queryset=None):
        # добавляем счетчик
        obj = super().get_object(queryset)
        obj.view_count = F('view_count') + 1
        obj.save(update_fields=['view_count'])
        obj.refresh_from_db()  # обновляем с обновленным счетчиком
        return obj

class BlogPostCreateView(CreateView):
    model = BlogPost
    template_name = 'blog/post_form.html'
    fields = ['title', 'content', 'preview', 'is_published']
    success_url = reverse_lazy('blog:post_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание новой записи'
        return context


class BlogPostUpdateView(UpdateView):
    model = BlogPost
    template_name = 'blog/post_form.html'
    fields = ['title', 'content', 'preview', 'is_published']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактирование: {self.object.title}'
        return context

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.object.pk})


class BlogPostDeleteView(DeleteView):
    model = BlogPost
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('blog:post_list')
    context_object_name = 'post'  # Добавляем это для ясности

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Убеждаемся, что объект доступен
        if hasattr(self, 'object') and self.object:
            context['title'] = f'Удаление: {self.object.title}'
        else:
            context['title'] = 'Удаление записи'
        return context
