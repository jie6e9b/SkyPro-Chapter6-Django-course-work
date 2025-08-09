from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("contacts/", views.contacts, name="contacts"),
    path("product/<int:product_id>/", views.product_detail, name="product_detail"),
    path("add_product/", views.add_product, name="add_product"),
 ]