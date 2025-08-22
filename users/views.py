from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.views.generic import CreateView, TemplateView, UpdateView
from django.urls import reverse_lazy
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm

User = get_user_model()


class RegisterView(CreateView):
    """Представление для регистрации пользователя"""
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        """Автоматический вход после успешной регистрации"""
        # Создаем пользователя вручную
        user = form.save()

        # Работаем с созданным пользователем
        self.send_welcome_email(user)
        login(self.request, user)
        messages.success(self.request, 'Регистрация прошла успешно! Добро пожаловать!')
        return redirect('catalog:index')

    def send_welcome_email(self, user):
        """Отправка приветственного email"""
        try:
            subject = 'Добро пожаловать в Skystore!'

            context = {
                'user': user,
                'site_name': 'Skystore',
                'site_url': self.request.build_absolute_uri('/'),
            }

            html_message = render_to_string('users/emails/welcome_email.html', context)
            plain_message = render_to_string('users/emails/welcome_email.txt', context)

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],  # Здесь используем user.email
                html_message=html_message,
                fail_silently=True,
            )

        except Exception as e:
            print(f"Ошибка отправки email: {e}")


    def dispatch(self, request, *args, **kwargs):
        """Если пользователь уже авторизован, перенаправляем на главную"""
        if request.user.is_authenticated:
            return redirect('catalog:index')
        return super().dispatch(request, *args, **kwargs)


class CustomLoginView(LoginView):
    """Кастомное представление для входа"""
    form_class = CustomAuthenticationForm
    template_name = 'users/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        """Перенаправление после успешного входа"""
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('catalog:index')

    def form_valid(self, form):
        """Добавляем сообщение об успешном входе"""
        messages.success(self.request, f'Добро пожаловать, {form.get_user().username}!')
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    """Кастомное представление для выхода"""
    next_page = 'catalog:index'

    def dispatch(self, request, *args, **kwargs):
        """Добавляем сообщение при выходе"""
        if request.user.is_authenticated:
            messages.info(request, 'Вы успешно вышли из системы')
        return super().dispatch(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, TemplateView):
    """Представление профиля пользователя"""
    template_name = 'users/profile.html'
    login_url = 'users:login'

    def get_context_data(self, **kwargs):
        """Добавляем дополнительный контекст для профиля"""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Профиль пользователя'
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Представление редактирования профиля пользователя"""
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile_edit.html'
    login_url = 'users:login'
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        """Возвращаем текущего пользователя"""
        return self.request.user

    def get_form_kwargs(self):
        """Передаем пользователя в форму"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Добавляем сообщение об успешном обновлении"""
        messages.success(self.request, 'Профиль успешно обновлен!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Добавляем дополнительный контекст"""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование профиля'
        return context