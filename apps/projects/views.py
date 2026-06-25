import os

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.portal_decorators import student_required, teacher_required
from apps.audit.utils import log_action

from .forms import ProjectForm
from .models import Project, ProjectImage

VALID_IMAGE_EXT = {'.jpg', '.jpeg', '.png', '.webp'}
MAX_IMAGE_BYTES = 5 * 1024 * 1024


def _validate_images(files):
    for f in files:
        ext = os.path.splitext(f.name)[1].lower()
        if ext not in VALID_IMAGE_EXT:
            raise ValueError(f'{f.name}: must be JPG, PNG, or WebP.')
        if f.size > MAX_IMAGE_BYTES:
            raise ValueError(f'{f.name}: must be under 5 MB.')


@student_required
def student_project(request):
    project, created = Project.objects.get_or_create(
        student=request.user,
        defaults={'title': 'My Project'},
    )
    form = ProjectForm(request.POST or None, request.FILES or None, instance=project)
    if request.method == 'POST' and form.is_valid():
        try:
            _validate_images(request.FILES.getlist('new_images'))
        except ValueError as e:
            messages.error(request, str(e))
            return render(request, 'student/project.html', {
                'project': project, 'form': form, 'active_nav': 'project',
            })
        project = form.save()
        for img_file in request.FILES.getlist('new_images'):
            ProjectImage.objects.create(project=project, image=img_file)
        log_action(request.user, 'project_updated', 'project', project.id, {'title': project.title})
        messages.success(request, 'Project saved.')
        return redirect('student:project')
    return render(request, 'student/project.html', {
        'project': project,
        'form': form,
        'active_nav': 'project',
    })


@teacher_required
def teacher_projects(request):
    projects = Project.objects.select_related('student', 'student__profile').prefetch_related('images')
    return render(request, 'teacher/projects.html', {
        'projects': projects,
        'active_nav': 'projects',
    })


@teacher_required
def teacher_project_detail(request, project_id):
    project = get_object_or_404(Project.objects.select_related('student', 'student__profile').prefetch_related('images'), id=project_id)
    return render(request, 'teacher/project_detail.html', {
        'project': project,
        'active_nav': 'projects',
    })
