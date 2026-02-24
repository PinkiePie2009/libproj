# projects/context_processors.py
from .models import Project

def moderation_count(request):
    """Добавляет количество проектов на модерации в контекст"""
    if request.user.is_authenticated and (hasattr(request.user, 'teacher') or request.user.is_staff):
        pending_count = Project.objects.filter(status='pending').count()
        return {'projects_pending': pending_count}
    return {'projects_pending': 0}