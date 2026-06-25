from django.conf import settings
from django.core.mail import send_mail

from apps.accounts.models import User
from apps.announcements.services import announcement_recipients


class EmailNotificationService:
    @staticmethod
    def _wants_email(user):
        profile = getattr(user, 'profile', None)
        if profile is not None and not profile.email_notifications:
            return False
        return bool(user.email)

    @staticmethod
    def _send(user, subject, message):
        if not EmailNotificationService._wants_email(user):
            return
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )

    @staticmethod
    def notify_assignment_published(assignment):
        students = User.objects.filter(type=User.UserType.STUDENT, status=User.UserStatus.ACTIVE)
        for student in students:
            EmailNotificationService._send(
                student,
                f'New assignment: {assignment.title}',
                (
                    f'Hello {student.first_name},\n\n'
                    f'A new assignment "{assignment.title}" has been posted.\n'
                    f'Due: {assignment.due_date:%B %d, %Y at %H:%M}\n\n'
                    f'Log in to view details and submit your work.'
                ),
            )

    @staticmethod
    def notify_grade_released(assignment):
        for sub in assignment.submissions.select_related('student'):
            if sub.score_obtained is not None:
                EmailNotificationService._send(
                    sub.student,
                    f'Grades released: {assignment.title}',
                    (
                        f'Hello {sub.student.first_name},\n\n'
                        f'Your grade for "{assignment.title}" has been released.\n'
                        f'Score: {sub.score_obtained} / {assignment.total_score}\n\n'
                        f'Log in to view feedback.'
                    ),
                )

    @staticmethod
    def notify_account_approved(user):
        EmailNotificationService._send(
            user,
            'Your account has been approved',
            f'Hello {user.first_name}, your Dev Academy account has been approved. You can now log in.',
        )

    @staticmethod
    def notify_account_rejected(user):
        EmailNotificationService._send(
            user,
            'Account registration update',
            f'Hello {user.first_name}, unfortunately your Dev Academy registration was not approved at this time.',
        )

    @staticmethod
    def notify_account_rejected_email(email, first_name):
        if not email:
            return
        send_mail(
            subject='Account registration update',
            message=f'Hello {first_name}, unfortunately your Dev Academy registration was not approved at this time.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=True,
        )

    @staticmethod
    def notify_announcement(announcement):
        for user in announcement_recipients(announcement).select_related('profile'):
            EmailNotificationService._send(
                user,
                f'New announcement: {announcement.title}',
                (
                    f'Hello {user.first_name},\n\n'
                    f'{announcement.title}\n\n'
                    f'{announcement.body}\n\n'
                    f'Log in to read more.'
                ),
            )

    @staticmethod
    def notify_submission_received(submission):
        teachers = User.objects.filter(type=User.UserType.TEACHER, status=User.UserStatus.ACTIVE)
        for teacher in teachers:
            EmailNotificationService._send(
                teacher,
                f'New submission: {submission.assignment.title}',
                (
                    f'{submission.student.get_full_name()} submitted "{submission.assignment.title}".\n'
                    f'Log in to review and grade.'
                ),
            )
