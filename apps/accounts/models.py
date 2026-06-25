import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('type', User.UserType.ADMIN)
        extra_fields.setdefault('status', User.UserStatus.ACTIVE)
        extra_fields.setdefault('email_verified', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class UserType(models.TextChoices):
        STUDENT = 'student', 'Student'
        TEACHER = 'teacher', 'Teacher'
        ADMIN = 'admin', 'Admin'

    class UserStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACTIVE = 'active', 'Active'
        SUSPENDED = 'suspended', 'Suspended'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=30, blank=True)
    type = models.CharField(max_length=20, choices=UserType.choices)
    status = models.CharField(max_length=20, choices=UserStatus.choices, default=UserStatus.PENDING)
    email_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_users'
    )
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_full_name()} ({self.email})'

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    def get_short_name(self):
        return self.first_name

    @property
    def email_verification_satisfied(self):
        if not settings.REQUIRE_EMAIL_VERIFICATION:
            return True
        return self.email_verified

    @property
    def is_active_account(self):
        return self.status == self.UserStatus.ACTIVE and self.email_verification_satisfied

    def get_portal_home_url(self):
        if self.type == self.UserType.STUDENT:
            return '/student/'
        if self.type == self.UserType.TEACHER:
            return '/teacher/'
        if self.type == self.UserType.ADMIN:
            return '/admin-panel/'
        return '/'


class InviteCode(models.Model):
    class Role(models.TextChoices):
        STUDENT = 'student', 'Student'
        TEACHER = 'teacher', 'Teacher'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        USED = 'used', 'Used'
        EXPIRED = 'expired', 'Expired'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True)
    role = models.CharField(max_length=20, choices=Role.choices)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_invite_codes')
    used_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name='used_invite_code'
    )
    expires_at = models.DateTimeField()
    is_single_use = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.code

    def is_valid(self):
        if self.status != self.Status.ACTIVE:
            return False
        if timezone.now() > self.expires_at:
            return False
        if self.is_single_use and self.used_by_id:
            return False
        return True


class EmailVerificationToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_tokens')
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.used and timezone.now() < self.expires_at


class PasswordResetToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.used and timezone.now() < self.expires_at
