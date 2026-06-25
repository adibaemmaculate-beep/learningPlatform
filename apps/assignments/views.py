from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.accounts.models import User
from apps.accounts.portal_decorators import student_required, teacher_required
from apps.audit.utils import log_action
from apps.courses.forms import get_active_course
from apps.notifications.services import EmailNotificationService

from .forms import AssignmentForm, GradeSubmissionForm, SubmissionForm
from .models import Assignment, AssignmentSubmission
from .services import (
    assignments_due_this_week,
    assignments_needing_attention,
    progress_dashboard_data,
    recent_graded_submission,
    student_grade_summary,
    student_overall_grade,
    student_roster_data,
    teacher_pending_submissions_count,
    get_active_students,
    get_published_assignments,
    get_student_submission,
)


# --- Student views ---

@student_required
def student_assignments(request):
    course = get_active_course()
    assignments = get_published_assignments(course)
    items = []
    for a in assignments:
        sub = get_student_submission(a, request.user)
        items.append({'assignment': a, 'submission': sub})
    return render(request, 'student/assignments.html', {
        'items': items,
        'active_nav': 'assignments',
    })


@student_required
def student_assignment_detail(request, assignment_id):
    assignment = get_object_or_404(
        Assignment.objects.select_related('created_by'),
        id=assignment_id,
        is_draft=False,
    )
    submission = get_student_submission(assignment, request.user)
    form = SubmissionForm(request.POST or None, request.FILES or None, assignment=assignment)
    if request.method == 'POST' and not submission and form.is_valid():
        sub = form.save(commit=False)
        sub.assignment = assignment
        sub.student = request.user
        sub.file_name = sub.file.name.split('/')[-1]
        sub.is_late = timezone.now() > assignment.due_date
        sub.save()
        log_action(request.user, 'assignment_submitted', 'submission', sub.id, {'assignment': assignment.title})
        EmailNotificationService.notify_submission_received(sub)
        messages.success(request, 'Assignment submitted successfully.')
        return redirect('student:assignment_detail', assignment_id=assignment.id)
    return render(request, 'student/assignment_detail.html', {
        'assignment': assignment,
        'submission': submission,
        'form': form,
        'active_nav': 'assignments',
    })


@student_required
def student_grades(request):
    summary = student_grade_summary(request.user)
    return render(request, 'student/grades.html', {
        'summary': summary,
        'active_nav': 'grades',
    })


# --- Teacher views ---

@teacher_required
def teacher_assignments(request):
    course = get_active_course()
    assignments = (
        Assignment.objects.filter(course=course).select_related('created_by')
        if course else Assignment.objects.none()
    )
    class_size = get_active_students().count()
    items = []
    for a in assignments:
        items.append({
            'assignment': a,
            'submission_count': a.submissions.count(),
            'class_size': class_size,
        })
    return render(request, 'teacher/assignments.html', {
        'items': items,
        'active_nav': 'assignments',
    })


@teacher_required
def teacher_assignment_create(request):
    course = get_active_course()
    if not course:
        messages.error(request, 'No active course found.')
        return redirect('teacher:assignments')
    form = AssignmentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        assignment = form.save(created_by=request.user)
        log_action(request.user, 'assignment_created', 'assignment', assignment.id, {'title': assignment.title})
        if not assignment.is_draft:
            EmailNotificationService.notify_assignment_published(assignment)
        messages.success(request, 'Assignment saved.')
        return redirect('teacher:assignment_detail', assignment_id=assignment.id)
    return render(request, 'teacher/assignment_form.html', {
        'form': form, 'editing': False, 'active_nav': 'assignments',
    })


@teacher_required
def teacher_assignment_edit(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    form = AssignmentForm(request.POST or None, instance=assignment)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Assignment updated.')
        return redirect('teacher:assignment_detail', assignment_id=assignment.id)
    return render(request, 'teacher/assignment_form.html', {
        'form': form, 'assignment': assignment, 'editing': True, 'active_nav': 'assignments',
    })


@teacher_required
def teacher_assignment_detail(request, assignment_id):
    assignment = get_object_or_404(Assignment.objects.select_related('created_by'), id=assignment_id)
    filter_status = request.GET.get('filter', 'all')
    students = get_active_students().select_related('profile')
    rows = []
    for s in students:
        sub = get_student_submission(assignment, s)
        if filter_status == 'submitted' and not sub:
            continue
        if filter_status == 'not_submitted' and sub:
            continue
        if filter_status == 'ungraded' and (not sub or sub.status != AssignmentSubmission.Status.SUBMITTED):
            continue
        rows.append({'student': s, 'submission': sub})
    return render(request, 'teacher/assignment_detail.html', {
        'assignment': assignment,
        'rows': rows,
        'filter_status': filter_status,
        'active_nav': 'assignments',
    })


@teacher_required
def teacher_grade_submission(request, assignment_id, submission_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    submission = get_object_or_404(AssignmentSubmission, id=submission_id, assignment=assignment)
    form = GradeSubmissionForm(
        request.POST or None,
        max_score=assignment.total_score,
        initial={'score_obtained': submission.score_obtained or 0, 'comments': submission.comments},
    )
    if request.method == 'POST' and form.is_valid():
        submission.score_obtained = form.cleaned_data['score_obtained']
        submission.comments = form.cleaned_data['comments']
        submission.status = AssignmentSubmission.Status.GRADED
        submission.graded_at = timezone.now()
        submission.graded_by = request.user
        submission.save()
        log_action(request.user, 'submission_graded', 'submission', submission.id, {
            'score': submission.score_obtained,
        })
        messages.success(request, 'Grade saved.')
        return redirect('teacher:assignment_detail', assignment_id=assignment.id)
    return render(request, 'teacher/grade_submission.html', {
        'assignment': assignment,
        'submission': submission,
        'form': form,
        'active_nav': 'assignments',
    })


@teacher_required
@require_POST
def teacher_release_grades(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    assignment.grades_released = True
    assignment.save(update_fields=['grades_released'])
    log_action(request.user, 'grades_released', 'assignment', assignment.id, {'title': assignment.title})
    EmailNotificationService.notify_grade_released(assignment)
    messages.success(request, f'Grades released for "{assignment.title}".')
    return redirect('teacher:assignment_detail', assignment_id=assignment.id)


@teacher_required
@require_POST
def teacher_assignment_delete(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    title = assignment.title
    assignment.delete()
    log_action(request.user, 'assignment_deleted', 'assignment', assignment_id, {'title': title})
    messages.success(request, f'Assignment "{title}" deleted.')
    return redirect('teacher:assignments')


@teacher_required
def teacher_students(request):
    q = request.GET.get('q', '').strip()
    roster = student_roster_data()
    if q:
        roster = [r for r in roster if q.lower() in r['student'].get_full_name().lower() or q.lower() in r['student'].email.lower()]
    return render(request, 'teacher/students.html', {
        'roster': roster,
        'search_q': q,
        'active_nav': 'students',
    })


@teacher_required
def teacher_student_detail(request, student_id):
    student = get_object_or_404(User, id=student_id, type=User.UserType.STUDENT)
    summary = student_grade_summary(student)
    project = None
    try:
        project = student.project
    except Exception:
        pass
    return render(request, 'teacher/student_detail.html', {
        'detail_student': student,
        'summary': summary,
        'project': project,
        'active_nav': 'students',
    })


@teacher_required
def teacher_progress(request):
    data = progress_dashboard_data()
    return render(request, 'teacher/progress.html', {
        'data': data,
        'active_nav': 'progress',
    })
