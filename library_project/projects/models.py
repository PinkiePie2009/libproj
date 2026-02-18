# projects/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.urls import reverse


class Subject(models.Model):
    """Предметы/дисциплины"""
    name = models.CharField(max_length=200, verbose_name="Название предмета")
    code = models.CharField(max_length=20, verbose_name="Код предмета", blank=True)
    description = models.TextField(verbose_name="Описание", blank=True)

    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"
        ordering = ['name']

    def __str__(self):
        return self.name

    def project_count(self):
        return self.projects.filter(status='published').count()


class Teacher(models.Model):
    """Преподаватели"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    department = models.CharField(max_length=200, verbose_name="Кафедра", blank=True)
    position = models.CharField(max_length=200, verbose_name="Должность", blank=True)
    bio = models.TextField(verbose_name="Биография", blank=True)

    class Meta:
        verbose_name = "Преподаватель"
        verbose_name_plural = "Преподаватели"

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

    def project_count(self):
        return self.supervised_projects.filter(status='published').count()


class Pupil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")

    class Meta:
        verbose_name = "Ученик"
        verbose_name_plural = "Ученики"

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

    def project_count(self):
        return self.projects.filter(status='published').count()


class Project(models.Model):
    """Учебный/исследовательский проект"""

    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('pending', 'На модерации'),
        ('published', 'Опубликован'),
        ('rejected', 'Отклонен'),
        ('archived', 'В архиве'),
    ]

    # Основная информация
    title = models.CharField(max_length=300, verbose_name="Название проекта")
    description = models.TextField(verbose_name="Описание")

    # Связи
    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        related_name='projects',
        verbose_name="Предмет"
    )
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        related_name='supervised_projects',
        verbose_name="Руководитель"
    )
    pupils = models.ManyToManyField(
        Pupil,
        related_name='projects',
        verbose_name="Авторы-ученики"
    )

    # Метаданные
    year = models.IntegerField(verbose_name="Год выполнения")
    keywords = models.CharField(
        max_length=500,
        verbose_name="Ключевые слова",
        help_text="Через запятую",
        blank=True
    )

    # Файлы проекта
    project_file = models.FileField(
        upload_to='projects/files/%Y/%m/%d/',
        verbose_name="Файл проекта",
        validators=[FileExtensionValidator(['pdf', 'doc', 'docx', 'zip', 'rar', '7z'])],
        null=True,
        blank=True
    )

    # Статистика и статус
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="Статус"
    )
    views = models.IntegerField(default=0, verbose_name="Просмотры")
    downloads = models.IntegerField(default=0, verbose_name="Скачивания")

    # Временные метки
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата публикации")

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['year', 'subject']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('project_detail', args=[str(self.id)])

    def increase_views(self):
        self.views += 1
        self.save(update_fields=['views'])

    def increase_downloads(self):
        self.downloads += 1
        self.save(update_fields=['downloads'])


class Comment(models.Model):
    """Комментарии к проектам"""
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Проект"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Пользователь"
    )
    text = models.TextField(verbose_name="Текст комментария")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата")

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ['-created_at']

    def __str__(self):
        return f"Комментарий от {self.user.username}"