from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.accounts.models import User

from .models import Profile


@receiver(post_save, sender=User)
def create_profile_on_approval(sender, instance, created, **kwargs):
    if instance.status == User.UserStatus.ACTIVE and instance.email_verification_satisfied:
        Profile.objects.get_or_create(user=instance)
