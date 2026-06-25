import os
import uuid

from django.db import models


def profile_pic_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    return f'profiles/{instance.user_id}/{uuid.uuid4().hex}{ext}'


class Profile(models.Model):
    class Theme(models.TextChoices):
        LIGHT = 'light', 'Light'
        DARK = 'dark', 'Dark'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    profile_pic = models.ImageField(upload_to=profile_pic_upload_path, blank=True, null=True)
    theme = models.CharField(max_length=10, choices=Theme.choices, default=Theme.LIGHT)
    email_notifications = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Profile: {self.user.get_full_name()}'
