import secrets

from django.urls import reverse


def generate_token():
    return secrets.token_urlsafe(32)


def get_verification_url(request, token):
    path = reverse('accounts:verify_email', kwargs={'token': token})
    return request.build_absolute_uri(path)


def get_reset_url(request, token):
    path = reverse('accounts:reset_password', kwargs={'token': token})
    return request.build_absolute_uri(path)
