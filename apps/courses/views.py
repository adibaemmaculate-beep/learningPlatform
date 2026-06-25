from datetime import datetime

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.accounts.portal_decorators import student_required, teacher_required
from apps.courses.forms import CourseMaterialForm, get_active_course
from apps.courses.models import CourseMaterial


@student_required
def student_materials(request):
    course = get_active_course()
    materials = []
    if course:
        materials = CourseMaterial.objects.filter(course=course, published=True)
    return render(request, 'student/course_materials.html', {
        'materials': materials,
        'course': course,
        'active_nav': 'materials',
    })


@teacher_required
def teacher_materials(request):
    course = get_active_course()
    materials = []
    if course:
        materials = CourseMaterial.objects.filter(course=course)
    return render(request, 'teacher/course_materials.html', {
        'materials': materials,
        'course': course,
        'active_nav': 'materials',
    })


@teacher_required
def material_create(request):
    course = get_active_course()
    if not course:
        messages.error(request, 'No active course found. Contact an administrator.')
        return redirect('teacher:materials')

    form = CourseMaterialForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        material = form.save(commit=False)
        material.course = course
        material.save()
        messages.success(request, f'Week {material.week} saved.')
        return redirect('teacher:materials')

    return render(request, 'teacher/material_form.html', {
        'form': form,
        'editing': False,
        'active_nav': 'materials',
    })


@teacher_required
def material_edit(request, material_id):
    material = get_object_or_404(CourseMaterial, id=material_id)
    form = CourseMaterialForm(request.POST or None, request.FILES or None, instance=material)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Week {material.week} updated.')
        return redirect('teacher:materials')

    return render(request, 'teacher/material_form.html', {
        'form': form,
        'material': material,
        'editing': True,
        'active_nav': 'materials',
    })


@teacher_required
@require_POST
def material_delete(request, material_id):
    material = get_object_or_404(CourseMaterial, id=material_id)
    week = material.week
    material.delete()
    messages.success(request, f'Week {week} deleted.')
    return redirect('teacher:materials')


@teacher_required
@require_POST
def material_toggle_publish(request, material_id):
    material = get_object_or_404(CourseMaterial, id=material_id)
    material.published = not material.published
    material.save(update_fields=['published'])
    status = 'published' if material.published else 'unpublished'
    messages.success(request, f'Week {material.week} {status}.')
    return redirect('teacher:materials')
