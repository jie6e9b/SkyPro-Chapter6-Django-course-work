from django.urls import path
from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("contacts/", views.ContactsView.as_view(), name="contacts"),
    path("product/<int:product_id>/", views.ProductDetailView.as_view(), name="product_detail"),
    path("add_product/", views.AddProductView.as_view(), name="add_product"),
    path("product/<int:product_id>/edit/", views.EditProductView.as_view(), name="edit_product"),
    path("product/<int:product_id>/delete/", views.DeleteProductView.as_view(), name="delete_product"),
]