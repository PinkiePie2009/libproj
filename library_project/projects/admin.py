from django.contrib import admin
from .models import Subject, Teacher, Student, Project


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    search_fields = ['name', 'code']


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['user', 'department', 'position']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['user', 'student_id', 'year']
    search_fields = ['user__username', 'student_id']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'year', 'status', 'views', 'created_at']
    list_filter = ['status', 'subject', 'year', 'created_at']
    search_fields = ['title', 'description', 'keywords']
    readonly_fields = ['views', 'created_at', 'updated_at']
    filter_horizontal = ['students']

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'subject', 'teacher', 'year', 'students', 'keywords')
        }),
        ('Файлы', {
            'fields': ('file',)
        }),
        ('Статус и статистика', {
            'fields': ('status', 'views', 'created_at', 'updated_at')
        }),
    )