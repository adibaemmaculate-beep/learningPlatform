from django.db.models import Q

from apps.accounts.models import User

from .models import Announcement, AnnouncementRead


def _visibility_q(user):
    q = Q(visibility=Announcement.Visibility.EVERYONE)
    if user.type == User.UserType.STUDENT:
        q |= Q(visibility=Announcement.Visibility.STUDENTS_ONLY)
        q |= Q(visibility=Announcement.Visibility.SPECIFIC_STUDENT, target_student=user)
    elif user.type == User.UserType.TEACHER:
        q |= Q(visibility=Announcement.Visibility.TEACHERS_ONLY)
    elif user.type == User.UserType.ADMIN:
        q |= Q(visibility=Announcement.Visibility.TEACHERS_ONLY)
        q |= Q(visibility=Announcement.Visibility.STUDENTS_ONLY)
    return q


def announcements_for_user(user):
    return Announcement.objects.filter(_visibility_q(user))


def unread_announcements(user, limit=5):
    read_ids = AnnouncementRead.objects.filter(user=user).values_list('announcement_id', flat=True)
    return announcements_for_user(user).exclude(id__in=read_ids)[:limit]


def mark_announcement_read(announcement, user):
    AnnouncementRead.objects.get_or_create(announcement=announcement, user=user)


def announcement_recipients(announcement):
    if announcement.visibility == Announcement.Visibility.EVERYONE:
        return User.objects.filter(status=User.UserStatus.ACTIVE)
    if announcement.visibility == Announcement.Visibility.STUDENTS_ONLY:
        return User.objects.filter(type=User.UserType.STUDENT, status=User.UserStatus.ACTIVE)
    if announcement.visibility == Announcement.Visibility.TEACHERS_ONLY:
        return User.objects.filter(type=User.UserType.TEACHER, status=User.UserStatus.ACTIVE)
    if announcement.visibility == Announcement.Visibility.SPECIFIC_STUDENT and announcement.target_student:
        return User.objects.filter(id=announcement.target_student_id, status=User.UserStatus.ACTIVE)
    return User.objects.none()
