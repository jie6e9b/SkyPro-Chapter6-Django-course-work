from django.db import models
from django.urls import reverse

class BlogPost(models.Model):
    """Model representing a blog post."""
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Содержимое')
    preview = models.ImageField(upload_to='blog/', verbose_name='Превью', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_published = models.BooleanField(default=False, verbose_name='Опубликовано')
    view_count = models.PositiveIntegerField(default=0, verbose_name='Количество просмотров')

    class Meta:
        verbose_name = 'Запись блога'
        verbose_name_plural = 'Записи блога'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Returns the URL to access a detail record for this blog post."""
        return reverse('blog:post_detail', args=[str(self.id)])
