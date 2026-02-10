from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator


class Subject(models.Model):
    """Предметы/дисциплины"""
    name = models.CharField(max_length=200, verbose_name="Название предмета")
    code = models.CharField(max_length=20, verbose_name="Код предмета", blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"


class Teacher(models.Model):
    """Преподаватели"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    department = models.CharField(max_length=200, verbose_name="Кафедра", blank=True)
    position = models.CharField(max_length=200, verbose_name="Должность", blank=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

    class Meta:
        verbose_name = "Преподаватель"
        verbose_name_plural = "Преподаватели"


class Student(models.Model):
    """Студенты"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    student_id = models.CharField(max_length=20, verbose_name="Номер студенческого", blank=True)
    year = models.IntegerField(verbose_name="Год поступления", blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

    class Meta:
        verbose_name = "Студент"
        verbose_name_plural = "Студенты"


class Project(models.Model):
    """Учебный/исследовательский проект"""

    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('published', 'Опубликован'),
        ('archived', 'В архиве'),
    ]

    title = models.CharField(max_length=300, verbose_name="Название проекта")
    description = models.TextField(verbose_name="Описание проекта")
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, verbose_name="Предмет")
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, verbose_name="Руководитель")
    year = models.IntegerField(verbose_name="Год выполнения")
    students = models.ManyToManyField(Student, verbose_name="Авторы-студенты")
    keywords = models.CharField(max_length=500, verbose_name="Ключевые слова", help_text="Через запятую", blank=True)

    # Файлы проекта
    file = models.FileField(
        upload_to='projects/files/%Y/%m/%d/',
        verbose_name="Файл проекта",
        validators=[FileExtensionValidator(['pdf', 'doc', 'docx', 'zip', 'rar', '7z'])]
    )

    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Статус")
    views = models.IntegerField(default=0, verbose_name="Просмотры")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ['-created_at']

    def increase_views(self):
        """Увеличивает счетчик просмотров"""
        self.views += 1
        self.save(update_fields=['views'])