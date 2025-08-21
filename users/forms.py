from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

# Получаем кастомную модель пользователя
User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """Кастомная форма регистрации"""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите email'
        })
    )
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+7XXXXXXXXXX'
        }),
        help_text='Необязательное поле. Формат: +7XXXXXXXXXX'
    )
    first_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите имя'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите фамилию'
        })
    )
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control'
        })
    )
    address = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите адрес'
        })
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'phone_number', 'first_name', 'last_name', 'avatar', 'address', 'password1',
                  'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя пользователя'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем стили к полям паролей
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Повторите пароль'
        })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует')
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            # Удаляем все символы кроме цифр и +
            cleaned_phone = ''.join(c for c in phone_number if c.isdigit() or c == '+')
            if not cleaned_phone.startswith('+') or len(cleaned_phone) < 11:
                raise forms.ValidationError('Неверный формат номера телефона')
        return phone_number


class CustomAuthenticationForm(AuthenticationForm):
    """Кастомная форма входа"""

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Имя пользователя',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пароль'
        })
    )


class UserProfileForm(forms.ModelForm):
    """Форма редактирования профиля пользователя"""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите email'
        })
    )
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+7XXXXXXXXXX'
        }),
        help_text='Необязательное поле. Формат: +7XXXXXXXXXX'
    )
    first_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите имя'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите фамилию'
        })
    )
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control'
        }),
        help_text='Загрузите новое изображение или оставьте поле пустым для сохранения текущего'
    )
    address = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Введите адрес',
            'rows': 3
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'first_name', 'last_name', 'avatar', 'address')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя пользователя'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Проверяем, что email не занят другим пользователем
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Проверяем, что имя пользователя не занято другим пользователем
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Пользователь с таким именем уже существует')
        return username

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            # Удаляем все символы кроме цифр и +
            cleaned_phone = ''.join(c for c in phone_number if c.isdigit() or c == '+')
            if not cleaned_phone.startswith('+') or len(cleaned_phone) < 11:
                raise forms.ValidationError('Неверный формат номера телефона')
        return phone_number