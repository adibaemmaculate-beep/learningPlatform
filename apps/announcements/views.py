import logging
from functools import wraps

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.models import User
from apps.accounts.portal_decorators import student_required, teacher_required
from apps.accounts.decorators import admin_required
from apps.audit.utils import log_action
from apps.notifications.services import EmailNotificationService

from .forms import AnnouncementForm
from .models import Announcement
from .services import announcements_for_user, mark_announcement_read, unread_announcements

logger = logging.getLogger(__name__)


def teacher_or_admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if request.user.type not in (User.UserType.TEACHER, User.UserType.ADMIN):
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return wrapper


@teacher_or_admin_required
def announcements_list(request):
    announcements = Announcement.objects.select_related('created_by', 'target_student').all()
    return render(request, 'teacher/announcements.html', {
        'announcements': announcements,
        'active_nav': 'announcements',
    })


@teacher_or_admin_required
def announcement_create(request):
    form = AnnouncementForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        announcement = form.save(commit=False)
        announcement.created_by = request.user
        announcement.save()
        log_action(request.user, 'announcement_created', 'announcement', announcement.id, {'title': announcement.title})
        try:
            EmailNotificationService.notify_announcement(announcement)
        except Exception:
            logger.exception('Failed to send notifications for announcement %s', announcement.id)
        messages.success(request, 'Announcement posted.')
        return redirect('teacher:announcements')
    return render(request, 'teacher/announcement_form.html', {
        'form': form,
        'active_nav': 'announcements',
    })


@teacher_or_admin_required
def announcement_detail(request, announcement_id):
    announcement = get_object_or_404(Announcement.objects.select_related('created_by', 'target_student'), id=announcement_id)
    reads = announcement.reads.select_related('user').order_by('-read_at')
    return render(request, 'teacher/announcement_detail.html', {
        'announcement': announcement,
        'reads': reads,
        'active_nav': 'announcements',
    })


@student_required
def student_announcement_detail(request, announcement_id):
    announcement = get_object_or_404(announcements_for_user(request.user), id=announcement_id)
    mark_announcement_read(announcement, request.user)
    return render(request, 'student/announcement_detail.html', {
        'announcement': announcement,
        'active_nav': 'dashboard',
    })


@student_required
def student_announcements(request):
    items = announcements_for_user(request.user)
    from .models import AnnouncementRead
    read_ids = set(AnnouncementRead.objects.filter(user=request.user).values_list('announcement_id', flat=True))
    return render(request, 'student/announcements.html', {
        'announcements': items,
        'read_ids': read_ids,
        'active_nav': 'announcements',
    })
