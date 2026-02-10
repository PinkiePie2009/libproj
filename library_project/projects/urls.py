# projects/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Основные страницы
    path('', views.index, name='index'),
    path('projects/', views.project_list, name='project_list'),
    path('projects/add/', views.project_add, name='project_add'),

    # Авторизация
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),

    # Сброс пароля (опционально)
    path('password-reset/',
         auth_views.PasswordResetView.as_view(template_name='projects/password_reset.html'),
         name='password_reset'),
]