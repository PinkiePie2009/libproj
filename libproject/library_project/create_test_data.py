# create_test_data.py
import os
import sys
import django

# Настройка Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Library_project.settings')
django.setup()

# Теперь импортируем модели
from django.contrib.auth.models import User
from projects.models import Subject, Teacher, Student, Project


def create_data():
    print("Создание тестовых данных...")

    # Проверяем, есть ли уже данные
    if Subject.objects.exists():
        print("Данные уже существуют. Очистите базу если нужно создать заново.")
        return

    # Создаем предметы
    subjects = [
        Subject(name='Алгоритмы', code='АИСД'),
        Subject(name='Базы данных', code='БД'),
        Subject(name='Веб-программирование', code='Веб'),
        Subject(name='Машинное обучение', code='МО'),
    ]
    for subject in subjects:
        subject.save()
        print(f"✓ Создан предмет: {subject.name}")

    # Создаем преподавателя
    teacher_user = User.objects.create_user(
        username='teacher1',
        password='teacher123',
        email='teacher@sfu.ru',
        first_name='Иван',
        last_name='Петров'
    )
    teacher = Teacher.objects.create(
        user=teacher_user,
        department='Кафедра ИТ',
        position='Доцент'
    )
    print(f"✓ Создан преподаватель: {teacher}")

    # Создаем студента
    student_user = User.objects.create_user(
        username='student1',
        password='student123',
        email='student@sfu.ru',
        first_name='Анна',
        last_name='Сидорова'
    )
    student = Student.objects.create(
        user=student_user,
        student_id='ФМИ-2024-001',
        group='ФМИ-21-1',
        enrollment_year=2024
    )
    print(f"✓ Создан студент: {student}")

    # Создаем проект
    project = Project.objects.create(
        title='Тестовый проект',
        description='Описание тестового проекта',
        subject=subjects[0],
        teacher=teacher,
        year=2024,
        keywords='тест, django',
        status='published'
    )
    project.students.add(student)
    print(f"✓ Создан проект: {project.title}")

    print("\n✅ Все данные успешно созданы!")
    print(f"   Всего предметов: {Subject.objects.count()}")
    print(f"   Всего преподавателей: {Teacher.objects.count()}")
    print(f"   Всего студентов: {Student.objects.count()}")
    print(f"   Всего проектов: {Project.objects.count()}")


if __name__ == '__main__':
    create_data()