# run_setup.py
import os
import sys
import subprocess


def setup_django():
    """Полная настройка проекта"""

    # 1. Проверяем текущую директорию
    print(f"Текущая директория: {os.getcwd()}")

    # 2. Проверяем наличие manage.py
    if not os.path.exists('manage.py'):
        print("❌ Ошибка: manage.py не найден!")
        print("   Запустите скрипт из папки с manage.py")
        return False

    # 3. Проверяем наличие settings
    settings_dir = 'Library_project'
    settings_file = os.path.join(settings_dir, 'settings.py')
    if not os.path.exists(settings_file):
        print(f"❌ Ошибка: {settings_file} не найден!")
        return False

    print(f"✅ Найден settings.py: {settings_file}")

    # 4. Устанавливаем переменные окружения
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_project.settings')

    # 5. Инициализируем Django
    try:
        import django
        django.setup()
        print("✅ Django успешно инициализирован!")
    except Exception as e:
        print(f"❌ Ошибка инициализации Django: {e}")
        return False

    # 6. Проверяем импорт моделей
    try:
        from projects.models import Subject
        print(f"✅ Модели успешно импортированы!")
        print(f"   Всего предметов: {Subject.objects.count()}")
    except Exception as e:
        print(f"❌ Ошибка импорта моделей: {e}")
        return False

    return True


if __name__ == '__main__':
    if setup_django():
        print("\n🎉 Все готово! Можно работать с базой данных.")
    else:
        print("\n❌ Настройка не удалась.")