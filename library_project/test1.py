# test1.py
import os
import sys
import django

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Устанавливаем переменную окружения с настройками
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_project.settings')

# Инициализируем Django
django.setup()

# Теперь можно импортировать модели
from projects.models import Subject, Teacher
from django.contrib.auth.models import User

# Создаем предметы если их нет
if Subject.objects.count() == 0:
    Subject.objects.create(name='Алгоритмы', code='АИСД')
    Subject.objects.create(name='Базы данных', code='БД')
    Subject.objects.create(name='Веб-программирование', code='Веб')
    print("Предметы созданы")

# Создаем преподавателя если его нет
if Teacher.objects.count() == 0 and User.objects.filter(username='teacher').exists():
    user = User.objects.get(username='teacher')
    Teacher.objects.create(user=user, department='ИТ', position='Доцент')
    print("Преподаватель создан")

print(f"Предметов: {Subject.objects.count()}")
print(f"Преподавателей: {Teacher.objects.count()}")
exit()