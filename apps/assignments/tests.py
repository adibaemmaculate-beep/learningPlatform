import os
import tempfile
from datetime import timedelta
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import User
from apps.courses.models import Course

from .models import Assignment, AssignmentSubmission
from .views import _submission_preview_kind


MEDIA_ROOT = tempfile.mkdtemp(prefix='assignment-tests-')


def uploaded_file(name='work.pdf', content=b'assignment content'):
    return SimpleUploadedFile(name, content, content_type='application/octet-stream')


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class AssignmentFlowTestCase(TestCase):
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
        self.other_student = User.objects.create_user(
            email='other@example.com',
            password='testpass123',
            first_name='Alan',
            last_name='Turing',
            type=User.UserType.STUDENT,
            status=User.UserStatus.ACTIVE,
            email_verified=True,
        )
        self.course = Course.objects.create(name='Programming', is_active=True)
        self.assignment = Assignment.objects.create(
            course=self.course,
            title='Week one exercise',
            instructions='Submit your work.',
            week=1,
            due_date=timezone.now() + timedelta(days=1),
            total_score=20,
            allowed_file_types=['.pdf', '.py', '.zip', '.ipynb', '.docx', '.mp4'],
            max_file_size_mb=2,
            is_draft=False,
            created_by=self.teacher,
        )

    def login_student(self, student=None):
        student = student or self.student
        self.client.login(email=student.email, password='testpass123')

    def login_teacher(self):
        self.client.login(email=self.teacher.email, password='testpass123')

    def create_submission(self, student=None, name='work.pdf'):
        return AssignmentSubmission.objects.create(
            assignment=self.assignment,
            student=student or self.student,
            file=uploaded_file(name),
            file_name=name,
            is_late=False,
        )


class StudentSubmissionTests(AssignmentFlowTestCase):
    @patch('apps.assignments.views.EmailNotificationService.notify_submission_received')
    def test_first_submission_creates_one_row(self, notify):
        self.login_student()
        response = self.client.post(
            reverse('student:assignment_detail', args=[self.assignment.id]),
            {'file': uploaded_file('first.pdf')},
        )

        self.assertRedirects(
            response,
            reverse('student:assignment_detail', args=[self.assignment.id]),
        )
        submission = AssignmentSubmission.objects.get()
        self.assertEqual(submission.student, self.student)
        self.assertEqual(submission.file_name, 'first.pdf')
        self.assertFalse(submission.is_late)
        notify.assert_called_once_with(submission)

    @patch('apps.assignments.views.EmailNotificationService.notify_submission_received')
    def test_replacement_updates_same_row_and_deletes_old_file(self, notify):
        submission = self.create_submission(name='old.pdf')
        original_id = submission.id
        old_path = submission.file.path
        old_time = timezone.now() - timedelta(days=2)
        AssignmentSubmission.objects.filter(id=submission.id).update(submitted_at=old_time)
        self.assertTrue(os.path.exists(old_path))
        self.login_student()

        response = self.client.post(
            reverse('student:assignment_detail', args=[self.assignment.id]),
            {'file': uploaded_file('new.pdf', b'new content')},
        )

        self.assertRedirects(
            response,
            reverse('student:assignment_detail', args=[self.assignment.id]),
        )
        submission.refresh_from_db()
        self.assertEqual(AssignmentSubmission.objects.count(), 1)
        self.assertEqual(submission.id, original_id)
        self.assertEqual(submission.file_name, 'new.pdf')
        self.assertGreater(submission.submitted_at, old_time)
        self.assertFalse(os.path.exists(old_path))
        self.assertTrue(os.path.exists(submission.file.path))
        notify.assert_called_once_with(submission)

    @patch('apps.assignments.views.EmailNotificationService.notify_submission_received')
    def test_replacement_recalculates_late_status(self, notify):
        submission = self.create_submission()
        self.assignment.due_date = timezone.now() - timedelta(minutes=1)
        self.assignment.save(update_fields=['due_date'])
        self.login_student()

        self.client.post(
            reverse('student:assignment_detail', args=[self.assignment.id]),
            {'file': uploaded_file('late.pdf')},
        )

        submission.refresh_from_db()
        self.assertTrue(submission.is_late)

    @patch('apps.assignments.views.EmailNotificationService.notify_submission_received')
    def test_graded_submission_cannot_be_replaced(self, notify):
        submission = self.create_submission()
        submission.status = AssignmentSubmission.Status.GRADED
        submission.score_obtained = 18
        submission.save(update_fields=['status', 'score_obtained'])
        original_file_name = submission.file.name
        self.login_student()

        response = self.client.post(
            reverse('student:assignment_detail', args=[self.assignment.id]),
            {'file': uploaded_file('blocked.pdf')},
        )

        self.assertRedirects(
            response,
            reverse('student:assignment_detail', args=[self.assignment.id]),
        )
        submission.refresh_from_db()
        self.assertEqual(submission.file.name, original_file_name)
        self.assertEqual(submission.score_obtained, 18)
        notify.assert_not_called()

    @patch('apps.assignments.views.EmailNotificationService.notify_submission_received')
    def test_invalid_replacement_keeps_existing_file(self, notify):
        submission = self.create_submission()
        original_file_name = submission.file.name
        self.login_student()

        response = self.client.post(
            reverse('student:assignment_detail', args=[self.assignment.id]),
            {'file': uploaded_file('malware.exe')},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'File type .exe not allowed.')
        submission.refresh_from_db()
        self.assertEqual(submission.file.name, original_file_name)
        notify.assert_not_called()

    def test_replacement_form_only_appears_for_ungraded_submission(self):
        submission = self.create_submission()
        self.login_student()
        url = reverse('student:assignment_detail', args=[self.assignment.id])

        response = self.client.get(url)
        self.assertContains(response, 'Replace submission')

        submission.status = AssignmentSubmission.Status.GRADED
        submission.save(update_fields=['status'])
        response = self.client.get(url)
        self.assertNotContains(response, '>Replace submission</button>')
        self.assertContains(response, 'can no longer be replaced')


class TeacherGradingTests(AssignmentFlowTestCase):
    def test_submission_row_links_to_grading_interface(self):
        submission = self.create_submission()
        self.login_teacher()

        response = self.client.get(
            reverse('teacher:assignment_detail', args=[self.assignment.id]),
        )

        grade_url = reverse(
            'teacher:grade_submission',
            args=[self.assignment.id, submission.id],
        )
        self.assertContains(response, grade_url)
        self.assertContains(response, 'Review &amp; grade')

    def test_grading_page_contains_inline_pdf_preview_and_form(self):
        submission = self.create_submission(name='solution.pdf')
        self.login_teacher()

        response = self.client.get(reverse(
            'teacher:grade_submission',
            args=[self.assignment.id, submission.id],
        ))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['preview_kind'], 'pdf')
        self.assertContains(response, 'PDF submission preview')
        self.assertContains(response, 'Grade and feedback')

    def test_preview_type_classification(self):
        submission = self.create_submission()
        expected = {
            'work.pdf': 'pdf',
            'demo.mp4': 'video',
            'answer.py': 'text',
            'analysis.ipynb': 'text',
            'archive.zip': 'download',
            'essay.docx': 'download',
        }
        for filename, preview_kind in expected.items():
            with self.subTest(filename=filename):
                submission.file_name = filename
                self.assertEqual(_submission_preview_kind(submission), preview_kind)

    def test_valid_grade_updates_submission(self):
        submission = self.create_submission()
        self.login_teacher()

        response = self.client.post(
            reverse(
                'teacher:grade_submission',
                args=[self.assignment.id, submission.id],
            ),
            {'score_obtained': 17, 'comments': 'Good work.'},
        )

        self.assertRedirects(
            response,
            reverse('teacher:assignment_detail', args=[self.assignment.id]),
        )
        submission.refresh_from_db()
        self.assertEqual(submission.score_obtained, 17)
        self.assertEqual(submission.comments, 'Good work.')
        self.assertEqual(submission.status, AssignmentSubmission.Status.GRADED)
        self.assertEqual(submission.graded_by, self.teacher)
        self.assertIsNotNone(submission.graded_at)

    def test_score_above_total_is_rejected(self):
        submission = self.create_submission()
        self.login_teacher()

        response = self.client.post(
            reverse(
                'teacher:grade_submission',
                args=[self.assignment.id, submission.id],
            ),
            {'score_obtained': 21, 'comments': ''},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Score cannot exceed 20.')
        submission.refresh_from_db()
        self.assertEqual(submission.status, AssignmentSubmission.Status.SUBMITTED)

    def test_submission_must_belong_to_assignment_in_grade_url(self):
        submission = self.create_submission()
        other_assignment = Assignment.objects.create(
            course=self.course,
            title='Other',
            week=2,
            due_date=timezone.now() + timedelta(days=2),
            allowed_file_types=['.pdf'],
            is_draft=False,
            created_by=self.teacher,
        )
        self.login_teacher()

        response = self.client.get(reverse(
            'teacher:grade_submission',
            args=[other_assignment.id, submission.id],
        ))

        self.assertEqual(response.status_code, 404)


class ProtectedSubmissionFileTests(AssignmentFlowTestCase):
    def test_student_can_access_own_file(self):
        submission = self.create_submission()
        self.login_student()

        response = self.client.get(
            reverse('student:submission_file', args=[submission.id]),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(b''.join(response.streaming_content), b'assignment content')
        self.assertIn('inline', response['Content-Disposition'])
        self.assertEqual(response['X-Frame-Options'], 'SAMEORIGIN')

    def test_student_cannot_access_another_students_file(self):
        submission = self.create_submission()
        self.login_student(self.other_student)

        response = self.client.get(
            reverse('student:submission_file', args=[submission.id]),
        )

        self.assertEqual(response.status_code, 404)

    def test_teacher_can_preview_and_download_submission(self):
        submission = self.create_submission()
        self.login_teacher()
        url = reverse('teacher:submission_file', args=[submission.id])

        preview_response = self.client.get(url)
        self.assertEqual(preview_response.status_code, 200)
        self.assertIn('inline', preview_response['Content-Disposition'])
        preview_response.close()

        download_response = self.client.get(f'{url}?download=1')
        self.assertEqual(download_response.status_code, 200)
        self.assertIn('attachment', download_response['Content-Disposition'])
        download_response.close()

    def test_student_cannot_use_teacher_file_endpoint(self):
        submission = self.create_submission()
        self.login_student()

        response = self.client.get(
            reverse('teacher:submission_file', args=[submission.id]),
        )

        self.assertRedirects(response, reverse('student:home'))

    def test_raw_submission_media_url_is_blocked(self):
        submission = self.create_submission()

        response = self.client.get(submission.file.url)

        self.assertEqual(response.status_code, 404)
