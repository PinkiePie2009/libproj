# projects/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm  # Добавляем импорт!
from .forms import CustomUserCreationForm


def index(request):
    """Главная страница"""
    return render(request, 'projects/index.html')


def project_list(request):
    """Список проектов"""
    projects = []
    return render(request, 'projects/project_list.html', {'projects': projects})


@login_required
def project_add(request):
    """Добавление проекта"""
    return render(request, 'projects/project_add.html')


def register_view(request):
    """Регистрация"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}! Регистрация успешна.')
            return redirect('index')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'projects/register.html', {'form': form})


def login_view(request):
    """Вход в систему"""
    if request.method == 'POST':
        # Используем стандартную AuthenticationForm
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {username}!')
                return redirect('index')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
    else:
        form = AuthenticationForm()

    # Добавляем классы к полям формы
    form.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Имя пользователя'})
    form.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Пароль'})

    return render(request, 'projects/login.html', {'form': form})


def logout_view(request):
    """Выход из системы"""
    logout(request)
    messages.info(request, 'Вы успешно вышли из системы.')
    return redirect('index')


@login_required
def profile_view(request):
    """Профиль пользователя"""
    return render(request, 'projects/profile.html', {'user': request.user})