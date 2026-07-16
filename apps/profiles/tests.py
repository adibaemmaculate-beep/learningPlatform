import io
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from PIL import Image

from apps.accounts.models import User
from apps.profiles.models import Profile

MEDIA_ROOT = tempfile.mkdtemp(prefix='profile-tests-')


def make_image(name='photo.jpg', fmt='JPEG', size=(40, 40), color='red'):
    buffer = io.BytesIO()
    Image.new('RGB', size, color=color).save(buffer, format=fmt)
    buffer.seek(0)
    content_type = {
        'JPEG': 'image/jpeg',
        'PNG': 'image/png',
        'WEBP': 'image/webp',
    }[fmt]
    return SimpleUploadedFile(name, buffer.read(), content_type=content_type)


def make_oversized_image(name='big.jpg'):
    # Create a valid JPEG larger than 10 MB by expanding compressed bytes.
    buffer = io.BytesIO()
    Image.new('RGB', (2500, 2500), color='blue').save(buffer, format='JPEG', quality=95)
    data = buffer.getvalue()
    target = 10 * 1024 * 1024 + 1024
    padded = data + (b'\x00' * (target - len(data)))
    return SimpleUploadedFile(name, padded, content_type='image/jpeg')


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class StudentProfileEditTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            email='student@example.com',
            password='testpass123',
            first_name='Ada',
            last_name='Lovelace',
            type=User.UserType.STUDENT,
            status=User.UserStatus.ACTIVE,
            email_verified=True,
        )
        self.profile, _ = Profile.objects.get_or_create(user=self.student)
        self.profile.bio = 'Original bio'
        self.profile.save(update_fields=['bio'])
        self.url = reverse('student:profile')
        self.client.login(email='student@example.com', password='testpass123')

    def test_student_can_edit_name_and_bio(self):
        response = self.client.post(self.url, {
            'first_name': 'Augusta',
            'last_name': 'King',
            'bio': 'Updated story',
        })
        self.assertRedirects(response, self.url)
        self.student.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.student.first_name, 'Augusta')
        self.assertEqual(self.student.last_name, 'King')
        self.assertEqual(self.profile.bio, 'Updated story')

    def test_blank_names_are_rejected(self):
        response = self.client.post(self.url, {
            'first_name': '   ',
            'last_name': 'King',
            'bio': 'Updated story',
        })
        self.assertEqual(response.status_code, 200)
        self.student.refresh_from_db()
        self.assertEqual(self.student.first_name, 'Ada')
        self.assertTrue(
            response.context['name_form'].errors.get('first_name'),
        )

    def test_jpeg_upload_accepted(self):
        response = self.client.post(self.url, {
            'first_name': 'Ada',
            'last_name': 'Lovelace',
            'bio': 'With photo',
            'profile_pic': make_image('portrait.jpeg', fmt='JPEG'),
        })
        self.assertRedirects(response, self.url)
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.profile_pic.name)
        self.assertTrue(
            self.profile.profile_pic.name.lower().endswith(('.jpg', '.jpeg'))
        )

    def test_png_and_webp_uploads_accepted(self):
        for name, fmt, ext in (
            ('pic.png', 'PNG', '.png'),
            ('pic.webp', 'WEBP', '.webp'),
        ):
            with self.subTest(name=name):
                response = self.client.post(self.url, {
                    'first_name': 'Ada',
                    'last_name': 'Lovelace',
                    'bio': 'ok',
                    'profile_pic': make_image(name, fmt=fmt),
                })
                self.assertRedirects(response, self.url)
                self.profile.refresh_from_db()
                self.assertTrue(self.profile.profile_pic.name.lower().endswith(ext))

    def test_invalid_extension_rejected(self):
        # Valid image bytes with a disallowed extension.
        bad_file = make_image('notes.gif', fmt='JPEG')
        response = self.client.post(self.url, {
            'first_name': 'Ada',
            'last_name': 'Lovelace',
            'bio': 'ok',
            'profile_pic': bad_file,
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Profile picture must be JPG, PNG, or WebP.')
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.profile_pic)

    def test_oversized_image_rejected(self):
        response = self.client.post(self.url, {
            'first_name': 'Ada',
            'last_name': 'Lovelace',
            'bio': 'ok',
            'profile_pic': make_oversized_image(),
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Profile picture must be under 10 MB.')
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.profile_pic)

    def test_name_update_without_new_image_keeps_existing_image(self):
        self.profile.profile_pic = make_image('keep.jpg')
        self.profile.save()
        old_name = self.profile.profile_pic.name

        response = self.client.post(self.url, {
            'first_name': 'Ada',
            'last_name': 'Byron',
            'bio': 'No new photo',
        })
        self.assertRedirects(response, self.url)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.profile_pic.name, old_name)
        self.student.refresh_from_db()
        self.assertEqual(self.student.last_name, 'Byron')

    def test_teacher_cannot_access_student_profile(self):
        teacher = User.objects.create_user(
            email='teacher@example.com',
            password='testpass123',
            first_name='Grace',
            last_name='Hopper',
            type=User.UserType.TEACHER,
            status=User.UserStatus.ACTIVE,
            email_verified=True,
        )
        Profile.objects.get_or_create(user=teacher)
        self.client.logout()
        self.client.login(email='teacher@example.com', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('teacher:home'))


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class AdminStudentProfileEditTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='testpass123',
            first_name='Admin',
            last_name='User',
            type=User.UserType.ADMIN,
            status=User.UserStatus.ACTIVE,
            email_verified=True,
            is_staff=True,
            is_superuser=True,
        )
        Profile.objects.get_or_create(user=self.admin)
        self.student = User.objects.create_user(
            email='student2@example.com',
            password='testpass123',
            first_name='Alan',
            last_name='Turing',
            type=User.UserType.STUDENT,
            status=User.UserStatus.ACTIVE,
            email_verified=True,
        )
        self.profile, _ = Profile.objects.get_or_create(user=self.student)
        self.profile.bio = 'Math'
        self.profile.save(update_fields=['bio'])
        self.url = reverse('admin_portal:student_profile_edit', args=[self.student.id])
        self.client.login(email='admin@example.com', password='testpass123')

    def test_admin_can_edit_student_name_and_photo(self):
        response = self.client.post(self.url, {
            'first_name': 'A.',
            'last_name': 'Turing',
            'profile_pic': make_image('admin-upload.jpg'),
        })
        self.assertRedirects(
            response,
            reverse('admin_portal:user_detail', args=[self.student.id]),
        )
        self.student.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.student.first_name, 'A.')
        self.assertEqual(self.student.last_name, 'Turing')
        self.assertTrue(self.profile.profile_pic.name)

    def test_admin_edit_rejects_blank_last_name(self):
        response = self.client.post(self.url, {
            'first_name': 'Alan',
            'last_name': '  ',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors.get('last_name'))
        self.student.refresh_from_db()
        self.assertEqual(self.student.last_name, 'Turing')

    def test_admin_cannot_edit_non_student(self):
        teacher = User.objects.create_user(
            email='teacher2@example.com',
            password='testpass123',
            first_name='Marie',
            last_name='Curie',
            type=User.UserType.TEACHER,
            status=User.UserStatus.ACTIVE,
            email_verified=True,
        )
        Profile.objects.get_or_create(user=teacher)
        url = reverse('admin_portal:student_profile_edit', args=[teacher.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_student_cannot_access_admin_edit(self):
        self.client.logout()
        self.client.login(email='student2@example.com', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('student:home'))

    def test_admin_edit_without_new_image_keeps_existing(self):
        self.profile.profile_pic = make_image('existing.jpg')
        self.profile.save()
        old_name = self.profile.profile_pic.name
        response = self.client.post(self.url, {
            'first_name': 'Alan',
            'last_name': 'Mathison',
        })
        self.assertRedirects(
            response,
            reverse('admin_portal:user_detail', args=[self.student.id]),
        )
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.profile_pic.name, old_name)
