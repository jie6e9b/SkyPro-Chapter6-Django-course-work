from django.contrib import admin
from .models import Category, Product, ContactInfo


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "category",)
    search_fields = ("name", "category__name")
    ordering = ("name",)


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = (
        "id", 
        "company_name", 
        "phone", 
        "email", 
        "is_active", 
        "updated_at"
    )
    list_filter = ("is_active", "created_at", "updated_at")
    search_fields = ("company_name", "phone", "email")
    ordering = ("-updated_at",)
    readonly_fields = ("created_at", "updated_at")
    
    fieldsets = (
        ("Основная информация", {
            "fields": ("company_name", "address", "phone", "email")
        }),
        ("Дополнительно", {
            "fields": ("working_hours", "description", "is_active")
        }),
        ("Системная информация", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )