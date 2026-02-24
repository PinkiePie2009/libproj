# projects/admin.py
from django.contrib import admin
from .models import Subject, Teacher, Pupil, Project, Comment


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'project_count']
    search_fields = ['name', 'code']

    def project_count(self, obj):
        return obj.projects.count()

    project_count.short_description = 'Проектов'


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['user', 'department', 'position', 'project_count']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']

    def project_count(self, obj):
        return obj.supervised_projects.count()

    project_count.short_description = 'Проектов'


@admin.register(Pupil)
class PupilAdmin(admin.ModelAdmin):
    list_display = ['user', 'project_count']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']

    def project_count(self, obj):
        return obj.projects.count()

    project_count.short_description = 'Проектов'


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'teacher', 'year', 'status', 'views', 'created_at']
    list_filter = ['status', 'subject', 'year']
    search_fields = ['title', 'description', 'keywords']
    readonly_fields = ['views', 'downloads', 'created_at', 'updated_at']
    filter_horizontal = ['pupils']
    actions = ['approve_projects']

    def approve_projects(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='published', published_at=timezone.now())
        self.message_user(request, f'{queryset.count()} проектов опубликовано')

    approve_projects.short_description = 'Опубликовать выбранные проекты'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'created_at']
    list_filter = ['created_at']