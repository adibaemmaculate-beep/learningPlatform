from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Send a test email using the configured EMAIL_BACKEND and SMTP settings'

    def add_arguments(self, parser):
        parser.add_argument(
            'recipient',
            help='Email address to send the test message to',
        )

    def handle(self, *args, **options):
        recipient = options['recipient']
        backend = settings.EMAIL_BACKEND
        from_email = settings.DEFAULT_FROM_EMAIL

        self.stdout.write(f'Backend: {backend}')
        self.stdout.write(f'From: {from_email}')
        self.stdout.write(f'To: {recipient}')

        try:
            send_mail(
                subject='Shamva Innovators — test email',
                message=(
                    'This is a test email from the Shamva Innovators learning platform.\n\n'
                    'If you received this, SMTP is configured correctly.'
                ),
                from_email=from_email,
                recipient_list=[recipient],
                fail_silently=False,
            )
        except Exception as exc:
            raise CommandError(f'Failed to send test email: {exc}') from exc

        self.stdout.write(self.style.SUCCESS(f'Test email sent to {recipient}'))
