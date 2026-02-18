# projects/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Главная
    path('', views.index, name='index'),

    # Проекты
    path('projects/', views.project_list, name='project_list'),
    path('projects/add/', views.project_add, name='project_add'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/<int:pk>/edit/', views.project_edit, name='project_edit'),
    path('projects/<int:pk>/download/', views.download_project, name='download_project'),

    # Авторизация
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),

    # API - ИСПРАВЛЕНО: используем правильное имя функции
    path('api/search/', views.search_api, name='search_api'),  # Было project_search_api, стало search_api
]