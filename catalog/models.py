from django.conf import settings
from django.db import models

import users.admin


class Category(models.Model):
    """ Модель категории товаров.
    Представляет категорию, к которой могут принадлежать товары.
    Каждая категория имеет название и описание.
    Attributes: name (str): Название категории (максимум 100 символов).
                description (str): Подробное описание категории."""
    
    name = models.CharField(max_length=100, verbose_name="Наименование")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")

    def __str__(self):
        """ Возвращает строковое представление категории.
        Returns: str: Название категории."""
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Product(models.Model):
    """ Модель товара в каталоге.
    Представляет товар с его основными характеристиками: название, описание,
    изображение, цена и привязка к категории. Автоматически отслеживает
    время создания и последнего обновления. Поддерживает систему модерации
    публикации товаров и привязку к пользователю-владельцу.
    
    Attributes:
        name (str): Название товара (максимум 100 символов).
        description (str): Подробное описание товара.
        image (ImageField): Изображение товара (необязательное поле).
        price (Decimal): Цена товара с точностью до 2 знаков после запятой.
        created_at (DateTime): Дата и время создания записи (автоматически).
        updated_at (DateTime): Дата и время последнего обновления (автоматически).
        publish (str): Статус публикации товара. Возможные значения:
            - 'pending': На модерации
            - 'published': Опубликован
            - 'rejected': Отказано в публикации
            - 'unpublished': Снят с публикации
        category (ForeignKey): Связь с категорией товара.
        owner (ForeignKey): Владелец продукта - пользователь, создавший товар.
            Автоматически заполняется при создании товара."""

    PUBLISH_CHOICES = [
        ('pending', 'На модерации'),
        ('published', 'Опубликован'),
        ('rejected', 'Отказано в публикации'),
        ('unpublished', 'Снят с публикации'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Наименование")
    description = models.TextField(verbose_name="Описание", blank=True, null=True)
    image = models.ImageField(upload_to='products/', blank=True, verbose_name="Изображение")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    publish = models.CharField(
        max_length=100,
        choices=PUBLISH_CHOICES,
        default='pending',
        verbose_name='Статус публикации')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Владелец продукта",
        related_name="products"
    )

    def __str__(self):
        """ Возвращает строковое представление категории.
        Returns: str: Название категории."""
        return self.name

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        permissions = [
            ('can_unpublish_product', 'Can unpublish product')
        ]

class ContactInfo(models.Model):
    """Модель для хранения контактной информации компании.
    
    Эта модель позволяет администратору управлять контактными данными
    через админ-панель Django без необходимости изменения кода.
    
    Attributes:
        company_name (str): Название компании.
        address (str): Адрес компании.
        phone (str): Контактный телефон.
        email (str): Электронная почта.
        working_hours (str): Часы работы.
        description (str): Дополнительная информация о компании.
        is_active (bool): Активность записи (для отображения на сайте).
        created_at (DateTime): Дата создания записи.
        updated_at (DateTime): Дата последнего обновления.
    """
    
    company_name = models.CharField(
        max_length=200, 
        verbose_name="Название компании",
        help_text="Официальное название компании"
    )
    address = models.TextField(
        verbose_name="Адрес", 
        help_text="Полный адрес компании"
    )
    phone = models.CharField(
        max_length=20,
        verbose_name="Телефон",
        help_text="Контактный телефон в формате +7 (XXX) XXX-XX-XX"
    )
    email = models.EmailField(
        verbose_name="Email",
        help_text="Электронная почта для связи"
    )
    working_hours = models.CharField(
        max_length=100,
        verbose_name="Часы работы",
        help_text="Например: Пн-Пт: 9:00-18:00, Сб-Вс: выходной"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание",
        help_text="Дополнительная информация о компании"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активно",
        help_text="Отображать эту информацию на сайте"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    def __str__(self):
        """Возвращает строковое представление контактной информации."""
        return f"{self.company_name} - {self.phone}"

    class Meta:
        verbose_name = 'Контактная информация'
        verbose_name_plural = 'Контактная информация'
        ordering = ['-created_at']