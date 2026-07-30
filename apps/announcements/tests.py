from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User

from .models import Announcement


class TeacherAnnouncementCreateTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            email='teacher@example.com',
            password='testpass123',
            first_name='Grace',
            last_name='Hopper',
            type=User.UserType.TEACHER,
            status=User.UserStatus.ACTIVE,
            email_verified=True,
        )
        self.student = User.objects.create_user(
            email='student@example.com',
            password='testpass123',
            first_name='Ada',
            last_name='Lovelace',
            type=User.UserType.STUDENT,
            status=User.UserStatus.ACTIVE,
            email_verified=True,
        )
        self.client.login(email=self.teacher.email, password='testpass123')
        self.url = reverse('teacher:announcement_create')

    @patch('apps.announcements.views.EmailNotificationService.notify_announcement')
    def test_teacher_can_post_announcement(self, notify):
        response = self.client.post(self.url, {
            'title': 'Class update',
            'body': 'The lab starts at 10.',
            'visibility': Announcement.Visibility.STUDENTS_ONLY,
            'target_student': '',
        })

        self.assertRedirects(response, reverse('teacher:announcements'))
        announcement = Announcement.objects.get()
        self.assertEqual(announcement.created_by, self.teacher)
        self.assertEqual(announcement.title, 'Class update')
        notify.assert_called_once_with(announcement)

    def test_required_field_errors_are_rendered(self):
        response = self.client.post(self.url, {
            'title': '',
            'body': '',
            'visibility': Announcement.Visibility.STUDENTS_ONLY,
            'target_student': '',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.', count=2)
        self.assertFalse(Announcement.objects.exists())

    def test_specific_student_requires_target(self):
        response = self.client.post(self.url, {
            'title': 'Private update',
            'body': 'Please see me after class.',
            'visibility': Announcement.Visibility.SPECIFIC_STUDENT,
            'target_student': '',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Select a student for targeted announcements.')
        self.assertFalse(Announcement.objects.exists())

    @patch(
        'apps.announcements.views.EmailNotificationService.notify_announcement',
        side_effect=RuntimeError('mail unavailable'),
    )
    def test_notification_failure_does_not_lose_announcement(self, notify):
        response = self.client.post(self.url, {
            'title': 'Saved update',
            'body': 'This should still be saved.',
            'visibility': Announcement.Visibility.EVERYONE,
            'target_student': '',
        })

        self.assertRedirects(response, reverse('teacher:announcements'))
        self.assertTrue(Announcement.objects.filter(title='Saved update').exists())
        notify.assert_called_once()
