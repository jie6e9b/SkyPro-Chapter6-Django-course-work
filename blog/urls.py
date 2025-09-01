from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.BlogPostListView.as_view(), name='post_list'),
    path('<int:post_id>/', views.BlogPostDetailView.as_view(), name='post_detail'),
    path('create/', views.BlogPostCreateView.as_view(), name='post_create'),
    path('<int:post_id>/edit/', views.BlogPostUpdateView.as_view(), name='post_update'),
    path('<int:post_id>/delete/', views.BlogPostDeleteView.as_view(), name='post_delete'),
    path('<int:post_id>/toggle-status/', views.toggle_blog_post_status, name='toggle_post_status'),
]