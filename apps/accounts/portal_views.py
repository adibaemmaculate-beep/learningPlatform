from django.shortcuts import render
from django.utils import timezone

from apps.accounts.portal_decorators import student_required, teacher_required
from apps.assignments.services import (
    assignments_due_this_week,
    assignments_needing_attention,
    recent_graded_submission,
    student_overall_grade,
    teacher_pending_submissions_count,
)
from apps.assignments.models import AssignmentSubmission
from apps.announcements.models import Announcement
from apps.courses.forms import get_active_course
from apps.courses.models import CourseMaterial
from apps.profiles.models import Profile


def _greeting_name(user):
    hour = timezone.localtime().hour
    if hour < 12:
        greeting = 'Good morning'
    elif hour < 17:
        greeting = 'Good afternoon'
    else:
        greeting = 'Good evening'
    return f'{greeting}, {user.first_name} 👋'


def _current_week_material(course):
    if not course:
        return None
    return CourseMaterial.objects.filter(course=course, published=True).order_by('-week').first()


@student_required
def student_home(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    course = get_active_course()
    current_week = _current_week_material(course)
    recent = recent_graded_submission(request.user, course)
    try:
        project = request.user.project
    except Exception:
        project = None
    return render(request, 'student/home.html', {
        'greeting': _greeting_name(request.user),
        'profile': profile,
        'course': course,
        'current_week': current_week,
        'due_this_week': assignments_due_this_week(request.user, course),
        'recent_grade': recent,
        'overall_grade_pct': student_overall_grade(request.user, course),
        'project': project,
        'active_nav': 'dashboard',
    })


@teacher_required
def teacher_home(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    course = get_active_course()
    material_count = published_count = 0
    if course:
        materials = CourseMaterial.objects.filter(course=course)
        material_count = materials.count()
        published_count = materials.filter(published=True).count()
    from apps.assignments.models import Assignment
    assignment_count = Assignment.objects.filter(course=course, is_draft=False).count() if course else 0
    submissions_week = AssignmentSubmission.objects.filter(
        submitted_at__gte=timezone.now() - timezone.timedelta(days=7),
        assignment__course=course,
    ).count() if course else 0
    return render(request, 'teacher/home.html', {
        'greeting': _greeting_name(request.user),
        'profile': profile,
        'course': course,
        'material_count': material_count,
        'published_count': published_count,
        'assignment_count': assignment_count,
        'submissions_this_week': submissions_week,
        'pending_submissions': teacher_pending_submissions_count(),
        'assignments_needing_attention': assignments_needing_attention(),
        'recent_announcements': Announcement.objects.select_related('created_by')[:5],
        'active_nav': 'dashboard',
    })
