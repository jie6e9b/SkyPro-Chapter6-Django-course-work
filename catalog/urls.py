from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('contacts/', views.ContactsView.as_view(), name='contacts'),
    path('add/', views.AddProductView.as_view(), name='add_product'),
    path('product/<int:product_id>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('product/<int:product_id>/edit/', views.EditProductView.as_view(), name='edit_product'),
    path('product/<int:product_id>/delete/', views.DeleteProductView.as_view(), name='delete_product'),
    path('product/<int:product_id>/toggle-status/', views.toggle_product_status, name='toggle_product_status'),
    path("category/<int:category_id>/products/", views.CategoryProductsView.as_view(), name="category_products"),
]
