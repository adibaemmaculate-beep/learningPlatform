import os

from django.core.management.base import BaseCommand

from apps.accounts.models import User
from apps.courses.models import Course


class Command(BaseCommand):
    help = 'Create the initial admin user and default course'

    def handle(self, *args, **options):
        email = os.getenv('SEED_ADMIN_EMAIL', 'admin@example.com')
        password = os.getenv('SEED_ADMIN_PASSWORD', 'changeme123')
        first_name = os.getenv('SEED_ADMIN_FIRST_NAME', 'Admin')
        last_name = os.getenv('SEED_ADMIN_LAST_NAME', 'User')

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'Admin user {email} already exists.'))
        else:
            User.objects.create_superuser(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
            self.stdout.write(self.style.SUCCESS(f'Created admin user: {email}'))

        course, created = Course.objects.get_or_create(
            name='AI & Coding — Cohort 1',
            defaults={
                'description': 'Middle school AI and coding program — Cohort 1',
                'is_active': True,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created course: {course.name}'))
        else:
            self.stdout.write(self.style.WARNING(f'Course already exists: {course.name}'))

        self.stdout.write(self.style.SUCCESS('Seed complete.'))
