# projects/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import FileResponse, JsonResponse
from .models import Project, Subject, Teacher, Pupil, Comment
from .forms import UserRegistrationForm, ProjectForm, CommentForm
from django.utils import timezone


def index(request):
    """Главная страница"""
    latest_projects = Project.objects.filter(status='published')[:6]
    popular_projects = Project.objects.filter(status='published').order_by('-views')[:3]

    # stats = {
    #     'projects': Project.objects.filter(status='published').count(),
    #     'pupils': Pupil.objects.count(),
    #     'teachers': Teacher.objects.count(),
    #     'subjects': Subject.objects.count(),
    # }

    context = {
        'latest_projects': latest_projects,
        'popular_projects': popular_projects,
        # 'stats': stats,
    }
    return render(request, 'projects/index.html', context)


def project_list(request):
    """Список всех проектов с фильтрацией"""
    # Для тестирования показываем все проекты (можно потом вернуть фильтр)
    projects = Project.objects.filter(status='published')

    # Поиск по ключевым словам
    query = request.GET.get('q')
    if query:
        projects = projects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(keywords__icontains=query)
        )

    # Фильтр по предмету
    subject_id = request.GET.get('subject')
    if subject_id:
        projects = projects.filter(subject_id=subject_id)

    # Фильтр по преподавателю
    teacher_id = request.GET.get('teacher')
    if teacher_id:
        projects = projects.filter(teacher_id=teacher_id)

    # Фильтр по году
    year = request.GET.get('year')
    if year:
        projects = projects.filter(year=year)

    # Сортировка по дате создания (новые сверху)
    projects = projects.order_by('-created_at')

    # Пагинация - 9 проектов на страницу
    paginator = Paginator(projects, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Получаем данные для фильтров
    subjects = Subject.objects.all()
    teachers = Teacher.objects.all()
    years = Project.objects.values_list('year', flat=True).distinct().order_by('-year')

    # Для отладки
    print(f"Всего проектов: {projects.count()}")
    print(f"Проектов на странице: {len(page_obj)}")

    context = {
        'page_obj': page_obj,
        'subjects': subjects,
        'teachers': teachers,
        'years': years,
        'current_filters': {
            'subject': subject_id,
            'teacher': teacher_id,
            'year': year,
            'q': query,
        }
    }
    return render(request, 'projects/project_list.html', context)


@login_required
def moderation_queue(request):
    """Очередь на модерацию (для преподавателей и админов)"""
    # Проверяем, является ли пользователь преподавателем или админом
    try:
        teacher = Teacher.objects.get(user=request.user)
        is_moderator = True
    except Teacher.DoesNotExist:
        if not request.user.is_staff:
            messages.error(request, 'У вас нет доступа к модерации.')
            return redirect('index')
        teacher = None
        is_moderator = True

    # Фильтры
    status_filter = request.GET.get('status', 'pending')
    projects = Project.objects.filter(status=status_filter).order_by('-created_at')

    # Статистика
    stats = {
        'pending': Project.objects.filter(status='pending').count(),
        'revision': Project.objects.filter(status='revision').count(),
        'published': Project.objects.filter(status='published').count(),
        'rejected': Project.objects.filter(status='rejected').count(),
    }

    context = {
        'projects': projects,
        'stats': stats,
        'current_status': status_filter,
        'teacher': teacher,
    }
    return render(request, 'projects/moderation_queue.html', context)


@login_required
def moderate_project(request, pk):
    """Модерация конкретного проекта"""
    project = get_object_or_404(Project, pk=pk)

    # Проверка прав
    try:
        teacher = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        if not request.user.is_staff:
            return HttpResponseForbidden("У вас нет прав на модерацию")
        teacher = None

    if request.method == 'POST':
        action = request.POST.get('action')
        comment = request.POST.get('comment', '')

        if action == 'approve':
            project.status = 'published'
            project.moderated_by = teacher if teacher else None
            project.moderation_comment = ''
            project.moderated_at = timezone.now()
            project.published_at = timezone.now()
            messages.success(request, f'Проект "{project.title}" опубликован!')

        elif action == 'reject':
            project.status = 'rejected'
            project.moderated_by = teacher if teacher else None
            project.moderation_comment = comment
            project.moderated_at = timezone.now()
            messages.warning(request, f'Проект "{project.title}" отклонен.')

        elif action == 'revision':
            project.status = 'revision'
            project.moderated_by = teacher if teacher else None
            project.moderation_comment = comment
            project.moderated_at = timezone.now()
            messages.info(request, f'Проект "{project.title}" отправлен на доработку.')

        project.save()
        return redirect('moderation_queue')

    context = {
        'project': project,
    }
    return render(request, 'projects/moderate_project.html', context)


@login_required
def my_submissions(request):
    """Мои отправленные проекты (для учеников)"""
    try:
        pupil = Pupil.objects.get(user=request.user)
        projects = Project.objects.filter(pupils=pupil).order_by('-created_at')
    except Pupil.DoesNotExist:
        projects = []
        messages.error(request, 'Только ученики могут отправлять проекты.')
        return redirect('index')

    context = {
        'projects': projects,
    }
    return render(request, 'projects/my_submissions.html', context)


@login_required
def resubmit_project(request, pk):
    """Повторная отправка проекта после доработки"""
    project = get_object_or_404(Project, pk=pk)

    # Проверяем, что пользователь - автор проекта
    if not project.pupils.filter(user=request.user).exists():
        messages.error(request, 'У вас нет прав на редактирование этого проекта.')
        return redirect('index')

    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            project = form.save(commit=False)
            project.status = 'pending'
            project.moderated_by = None
            project.moderation_comment = ''
            project.save()
            messages.success(request, 'Проект отправлен на повторную модерацию!')
            return redirect('my_submissions')
    else:
        form = ProjectForm(instance=project)

    context = {
        'form': form,
        'project': project,
        'is_resubmit': True,
    }
    return render(request, 'projects/project_add.html', context)


@login_required
def project_add(request):
    """Добавление нового проекта (только для учеников)"""
    try:
        pupil = Pupil.objects.get(user=request.user)
    except Pupil.DoesNotExist:
        messages.error(request, 'Только ученики могут добавлять проекты.')
        return redirect('index')

    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.status = 'pending'  # Отправляем на модерацию
            project.save()
            project.pupils.add(pupil)
            messages.success(request, 'Проект успешно отправлен на модерацию! Вы получите уведомление после проверки.')
            return redirect('my_submissions')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ProjectForm()

    subjects = Subject.objects.all()
    teachers = Teacher.objects.all()

    context = {
        'form': form,
        'subjects': subjects,
        'teachers': teachers,
    }
    return render(request, 'projects/project_add.html', context)


@login_required
def project_edit(request, pk):
    """Редактирование проекта"""
    project = get_object_or_404(Project, pk=pk)

    if not project.pupils.filter(user=request.user).exists() and not request.user.is_staff:
        messages.error(request, 'У вас нет прав на редактирование этого проекта.')
        return redirect('project_detail', pk=project.pk)

    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            project = form.save()
            messages.success(request, 'Проект успешно обновлен!')
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)

    context = {
        'form': form,
        'project': project,
        'is_edit': True,
    }
    return render(request, 'projects/project_add.html', context)


def download_project(request, pk):
    """Скачивание файла проекта"""
    project = get_object_or_404(Project, pk=pk, status='published')

    if project.project_file:
        project.increase_downloads()
        return FileResponse(project.project_file, as_attachment=True)
    else:
        messages.error(request, 'Файл проекта не найден.')
        return redirect('project_detail', pk=project.pk)


def register_view(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.username}! Регистрация успешна.')
                return redirect('index')
            except Exception as e:
                messages.error(request, f'Ошибка при сохранении: {e}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserRegistrationForm()

    return render(request, 'projects/register.html', {'form': form})



def logout_view(request):
    """Выход пользователя"""
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('index')


@login_required
def profile_view(request):
    """Профиль пользователя"""
    try:
        pupil = Pupil.objects.get(user=request.user)
        projects = Project.objects.filter(pupils=pupil)
    except Pupil.DoesNotExist:
        pupil = None
        projects = []

    try:
        teacher = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        teacher = None

    context = {
        'pupil': pupil,
        'teacher': teacher,
        'projects': projects,
    }
    return render(request, 'projects/profile.html', context)


def search_api(request):
    """API для поиска (AJAX)"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})

    projects = Project.objects.filter(
        status='published',
        title__icontains=query
    )[:5]

    results = [{
        'id': p.id,
        'title': p.title,
        'year': p.year,
        'url': f'/projects/{p.id}/'
    } for p in projects]

    return JsonResponse({'results': results})


def project_detail(request, pk):
    """Детальная страница проекта"""
    project = get_object_or_404(Project, pk=pk)
    project.increase_views()

    # Для отладки - выведем информацию
    print(f"Запрошен проект: {project.title}")
    print(f"Шаблон: projects/project_detail.html")

    similar_projects = Project.objects.filter(
        subject=project.subject,
        status='published'
    ).exclude(pk=project.pk)[:3]

    comments = project.comments.all()

    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.project = project
            comment.user = request.user
            comment.save()
            messages.success(request, 'Комментарий добавлен!')
            return redirect('project_detail', pk=project.pk)
    else:
        comment_form = CommentForm()

    context = {
        'project': project,
        'similar_projects': similar_projects,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'projects/project_detail.html', context)


def login_view(request):
    """Вход пользователя"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'С возвращением, {username}!')
            return redirect('index')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')

    return render(request, 'projects/login.html')