from django import forms
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from .models import Product
import os


# Константы с запрещенными словами
FORBIDDEN_WORDS = [
    'казино', 'криптовалюта', 'радар', 'rolex', 'viagra', 'bitcoin',
    'gambling', 'casino', 'porn', 'sex', 'наркотики', 'drugs',
    'взлом', 'hack', 'крипта', 'crypto', 'ставки', 'betting'
]

# Константы для валидации изображений
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 МБ в байтах
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png']
ALLOWED_CONTENT_TYPES = ['image/jpeg', 'image/png']


def validate_image_file(image):
    """
    Валидатор для проверки изображений:
    - Проверяет формат файла (JPEG, PNG)
    - Проверяет размер файла (не более 5 МБ)
    - Проверяет, что файл действительно является изображением
    """
    if not image:
        return

    # Проверка размера файла
    if image.size > MAX_FILE_SIZE:
        size_mb = round(image.size / (1024 * 1024), 2)
        raise ValidationError(
            f'Размер файла ({size_mb} МБ) превышает максимально допустимый размер 5 МБ'
        )

    # Проверка расширения файла
    file_extension = os.path.splitext(image.name)[1].lower()
    if file_extension not in ALLOWED_IMAGE_EXTENSIONS:
        allowed_formats = ', '.join(ALLOWED_IMAGE_EXTENSIONS)
        raise ValidationError(
            f'Неподдерживаемый формат файла. '
            f'Разрешены только: {allowed_formats}'
        )

    # Проверка MIME-типа
    if hasattr(image, 'content_type') and image.content_type:
        if image.content_type not in ALLOWED_CONTENT_TYPES:
            raise ValidationError(
                'Файл должен быть изображением в формате JPEG или PNG'
            )

    # Дополнительная проверка, что файл действительно является изображением
    try:
        # Попытка получить размеры изображения
        width, height = get_image_dimensions(image)
        if width is None or height is None:
            raise ValidationError(
                'Загруженный файл не является корректным изображением'
            )

        # Проверка минимальных размеров (опционально)
        if width < 100 or height < 100:
            raise ValidationError(
                'Изображение слишком маленькое. '
                'Минимальный размер: 100x100 пикселей'
            )

        # Проверка максимальных размеров (опционально)
        if width > 5000 or height > 5000:
            raise ValidationError(
                'Изображение слишком большое. '
                'Максимальный размер: 5000x5000 пикселей'
            )

    except Exception:
        raise ValidationError(
            'Не удается обработать загруженное изображение. '
            'Убедитесь, что файл не поврежден'
        )


class ProductForm(forms.ModelForm):
    """Форма для создания и редактирования продуктов"""

    class Meta:
        model = Product
        # Исключаем поле owner из формы - оно будет заполняться автоматически
        fields = ['name', 'description', 'price', 'category', 'image']  # Убрали publish из обязательных полей
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название продукта',
                'maxlength': 200,
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Введите описание продукта',
                'rows': 5,
                'style': 'resize: vertical;'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'min': '0',
                'step': '0.01',
                'required': True
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/png',
                'capture': 'environment'
            })
        }
        labels = {
            'name': 'Название продукта',
            'description': 'Описание',
            'price': 'Цена (₽)',
            'category': 'Категория',
            'image': 'Изображение'
        }
        help_texts = {
            'name': 'Максимум 200 символов. Обязательное поле.',
            'description': 'Подробное описание продукта',
            'price': 'Укажите цену в рублях. Обязательное поле.',
            'category': 'Выберите категорию товара. Обязательное поле.',
            'image': 'Поддерживаются форматы: JPEG, PNG. Максимальный размер: 5 МБ'
        }

    def __init__(self, *args, **kwargs):
        # Извлекаем информацию о пользователе из kwargs
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Добавляем валидатор для поля изображения
        self.fields['image'].validators.append(validate_image_file)

        # Делаем обязательные поля явно обязательными
        self.fields['name'].required = True
        self.fields['price'].required = True
        self.fields['category'].required = True

        # Добавляем поле publish только для аутентифицированных модераторов
        if (self.user and
                hasattr(self.user, 'is_authenticated') and
                self.user.is_authenticated and
                self.user.has_perm('catalog.can_unpublish_product') and
                hasattr(Product, 'PUBLISH_CHOICES')):

            # Определяем начальное значение
            initial_value = 'pending'
            if self.instance and self.instance.pk and hasattr(self.instance, 'publish'):
                initial_value = self.instance.publish

            self.fields['publish'] = forms.ChoiceField(
                choices=Product.PUBLISH_CHOICES,
                initial=initial_value,
                widget=forms.Select(attrs={'class': 'form-select'}),
                label='Статус публикации',
                help_text='Выберите статус публикации товара',
                required=True
            )

    def clean_name(self):
        """Валидация названия продукта на запрещенные слова"""
        name = self.cleaned_data.get('name', '')
        if not name:
            raise ValidationError('Название продукта обязательно для заполнения')

        name_lower = name.lower()

        for word in FORBIDDEN_WORDS:
            if word in name_lower:
                raise ValidationError(
                    f'Название продукта не может содержать запрещенное слово: "{word}"'
                )

        return name

    def clean_description(self):
        """Валидация описания продукта на запрещенные слова"""
        description = self.cleaned_data.get('description', '')
        if description:  # Описание не обязательное
            description_lower = description.lower()

            for word in FORBIDDEN_WORDS:
                if word in description_lower:
                    raise ValidationError(
                        f'Описание продукта не может содержать запрещенное слово: "{word}"'
                    )

        return description

    def clean_image(self):
        """Дополнительная валидация изображения"""
        image = self.cleaned_data.get('image')

        # Валидатор уже вызван через validators, но можно добавить дополнительные проверки
        if image:
            # Дополнительная бизнес-логика валидации изображений, если нужна
            pass

        return image

    def clean_price(self):
        """Валидация цены продукта"""
        price = self.cleaned_data.get('price')

        if price is None:
            raise ValidationError('Цена обязательна для заполнения')

        if price < 0:
            raise ValidationError(
                'Цена продукта не может быть отрицательной'
            )

        if price > 1000000:
            raise ValidationError(
                'Цена продукта не может превышать 1 000 000 рублей'
            )

        return price

    def save(self, commit=True):
        """Переопределяем сохранение для установки статуса по умолчанию"""
        instance = super().save(commit=False)

        # Если поле publish не было установлено (обычный пользователь), устанавливаем 'pending'
        if not hasattr(instance, 'publish') or not instance.publish:
            instance.publish = 'pending'

        if commit:
            instance.save()
        return instance