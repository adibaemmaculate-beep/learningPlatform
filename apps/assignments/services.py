from datetime import timedelta

from django.db.models import Avg, Count, Q
from django.utils import timezone

from apps.accounts.models import User
from apps.courses.forms import get_active_course

from .models import Assignment, AssignmentSubmission


def get_active_students():
    return User.objects.filter(type=User.UserType.STUDENT, status=User.UserStatus.ACTIVE)


def get_published_assignments(course=None):
    course = course or get_active_course()
    if not course:
        return Assignment.objects.none()
    return Assignment.objects.filter(course=course, is_draft=False).select_related('created_by')


def get_student_submission(assignment, student):
    try:
        return AssignmentSubmission.objects.get(assignment=assignment, student=student)
    except AssignmentSubmission.DoesNotExist:
        return None


def student_overall_grade(student, course=None):
    assignments = get_published_assignments(course).filter(grades_released=True)
    earned = 0
    possible = 0
    for a in assignments:
        sub = get_student_submission(a, student)
        if sub and sub.score_obtained is not None:
            earned += sub.score_obtained
            possible += a.total_score
    if possible == 0:
        return None
    return round(earned / possible * 100, 1)


def student_grade_summary(student, course=None):
    assignments = get_published_assignments(course)
    rows = []
    earned = 0
    possible = 0
    for a in assignments:
        sub = get_student_submission(a, student)
        score_display = '—'
        if sub and sub.score_obtained is not None and a.grades_released:
            score_display = f'{sub.score_obtained} / {a.total_score}'
            earned += sub.score_obtained
            possible += a.total_score
        elif sub and not a.grades_released:
            score_display = 'Pending release'
        rows.append({
            'assignment': a,
            'submission': sub,
            'score_display': score_display,
        })
    pct = round(earned / possible * 100, 1) if possible else None
    return {'rows': rows, 'earned': earned, 'possible': possible, 'percentage': pct}


def assignments_due_this_week(student, course=None):
    now = timezone.now()
    week_end = now + timedelta(days=7)
    assignments = get_published_assignments(course).filter(due_date__gte=now, due_date__lte=week_end)
    result = []
    for a in assignments:
        sub = get_student_submission(a, student)
        if sub:
            status = 'Submitted' if not sub.is_late else 'Late'
            if sub.status == AssignmentSubmission.Status.GRADED and a.grades_released:
                status = 'Graded'
        else:
            status = 'Not Started'
        result.append({'assignment': a, 'submission': sub, 'status': status})
    return result


def recent_graded_submission(student, course=None):
    subs = AssignmentSubmission.objects.filter(
        student=student,
        assignment__grades_released=True,
        score_obtained__isnull=False,
        assignment__course=course or get_active_course(),
    ).select_related('assignment', 'assignment__created_by').order_by('-graded_at')[:1]
    return subs.first()


def teacher_pending_submissions_count():
    return AssignmentSubmission.objects.filter(
        status=AssignmentSubmission.Status.SUBMITTED,
        assignment__is_draft=False,
    ).count()


def assignments_needing_attention():
    now = timezone.now()
    return Assignment.objects.filter(
        is_draft=False,
        due_date__lt=now,
        grades_released=False,
    ).annotate(
        ungraded=Count('submissions', filter=Q(submissions__status=AssignmentSubmission.Status.SUBMITTED))
    ).filter(ungraded__gt=0)[:5]


def student_roster_data(course=None):
    students = get_active_students().select_related('profile')
    roster = []
    for s in students:
        summary = student_grade_summary(s, course)
        submitted_count = AssignmentSubmission.objects.filter(
            student=s, assignment__course=course or get_active_course(), assignment__is_draft=False
        ).count()
        roster.append({
            'student': s,
            'grade_pct': summary['percentage'],
            'submitted_count': submitted_count,
            'last_activity': AssignmentSubmission.objects.filter(student=s).order_by('-submitted_at').values_list('submitted_at', flat=True).first(),
        })
    roster.sort(key=lambda x: (x['grade_pct'] is None, -(x['grade_pct'] or 0)))
    return roster


def progress_dashboard_data(course=None):
    course = course or get_active_course()
    assignments = get_published_assignments(course)
    students = get_active_students()
    student_count = students.count()

    assignment_stats = []
    for a in assignments:
        subs = a.submissions.all()
        submitted = subs.count()
        on_time = subs.filter(is_late=False).count()
        late = subs.filter(is_late=True).count()
        not_submitted = max(student_count - submitted, 0)
        avg_score = subs.filter(score_obtained__isnull=False).aggregate(avg=Avg('score_obtained'))['avg']
        assignment_stats.append({
            'assignment': a,
            'submitted': submitted,
            'on_time': on_time,
            'late': late,
            'not_submitted': not_submitted,
            'avg_score': round(avg_score, 1) if avg_score else None,
            'avg_pct': round(avg_score / a.total_score * 100, 1) if avg_score else None,
        })

    roster = student_roster_data(course)
    top = [r for r in roster if r['grade_pct'] is not None][:3]
    bottom = [r for r in reversed(roster) if r['grade_pct'] is not None][:3]

    return {
        'assignment_stats': assignment_stats,
        'student_count': student_count,
        'top_performers': top,
        'needs_support': bottom,
    }
