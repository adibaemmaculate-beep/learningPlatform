import secrets
import string
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from apps.audit.utils import log_action

from .forms import (
    ForgotPasswordForm,
    LoginForm,
    RegisterForm,
    ResetPasswordForm,
)
from .models import EmailVerificationToken, InviteCode, PasswordResetToken, User
from .tokens import generate_token, get_verification_url, get_reset_url


def _send_verification_email(user, request):
    token_str = generate_token()
    EmailVerificationToken.objects.create(
        user=user,
        token=token_str,
        expires_at=timezone.now() + timedelta(hours=48),
    )
    verify_url = get_verification_url(request, token_str)
    send_mail(
        subject='Verify your email address',
        message=f'Please verify your email by visiting: {verify_url}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


@require_http_methods(['GET', 'POST'])
def login_view(request):
    if request.user.is_authenticated and request.user.is_active_account:
        return redirect(request.user.get_portal_home_url())

    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(request, email=form.cleaned_data['email'], password=form.cleaned_data['password'])
        if user is None:
            form.add_error(None, 'Invalid email or password.')
        elif settings.REQUIRE_EMAIL_VERIFICATION and not user.email_verified:
            form.add_error(None, 'Please verify your email before logging in.')
        elif user.status == User.UserStatus.PENDING:
            form.add_error(None, 'Your account is pending admin approval.')
        elif user.status == User.UserStatus.SUSPENDED:
            form.add_error(None, 'Your account has been suspended.')
        else:
            login(request, user)
            return redirect(user.get_portal_home_url())

    return render(request, 'auth/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('accounts:login')


@require_http_methods(['GET', 'POST'])
def register_view(request):
    if request.user.is_authenticated:
        return redirect(request.user.get_portal_home_url())

    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        invite = form.cleaned_data['invite']
        require_verification = settings.REQUIRE_EMAIL_VERIFICATION
        user = User.objects.create_user(
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password'],
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            phone_number=form.cleaned_data.get('phone_number', ''),
            type=invite.role,
            status=User.UserStatus.PENDING,
            email_verified=not require_verification,
            email_verified_at=None if require_verification else timezone.now(),
        )
        invite.used_by = user
        if invite.is_single_use:
            invite.status = InviteCode.Status.USED
        invite.save()
        if require_verification:
            _send_verification_email(user, request)
            return render(request, 'auth/verify_email_sent.html', {'email': user.email})
        return render(request, 'auth/registration_pending.html')

    return render(request, 'auth/register.html', {'form': form})


def verify_email_view(request, token):
    try:
        token_obj = EmailVerificationToken.objects.select_related('user').get(token=token)
    except EmailVerificationToken.DoesNotExist:
        return render(request, 'auth/verify_email.html', {'success': False})

    if not token_obj.is_valid():
        return render(request, 'auth/verify_email.html', {'success': False})

    user = token_obj.user
    user.email_verified = True
    user.email_verified_at = timezone.now()
    user.save(update_fields=['email_verified', 'email_verified_at'])
    token_obj.used = True
    token_obj.save(update_fields=['used'])

    return render(request, 'auth/verify_email.html', {'success': True})


@require_http_methods(['GET', 'POST'])
def forgot_password_view(request):
    form = ForgotPasswordForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            pass
        else:
            token_str = generate_token()
            PasswordResetToken.objects.create(
                user=user,
                token=token_str,
                expires_at=timezone.now() + timedelta(hours=24),
            )
            reset_url = get_reset_url(request, token_str)
            send_mail(
                subject='Reset your password',
                message=f'Reset your password by visiting: {reset_url}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        return render(request, 'auth/forgot_password.html', {'form': form, 'sent': True})

    return render(request, 'auth/forgot_password.html', {'form': form, 'sent': False})


@require_http_methods(['GET', 'POST'])
def reset_password_view(request, token):
    try:
        token_obj = PasswordResetToken.objects.select_related('user').get(token=token)
    except PasswordResetToken.DoesNotExist:
        return render(request, 'auth/reset_password.html', {'valid': False})

    if not token_obj.is_valid():
        return render(request, 'auth/reset_password.html', {'valid': False})

    form = ResetPasswordForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = token_obj.user
        user.set_password(form.cleaned_data['password'])
        user.save()
        token_obj.used = True
        token_obj.save(update_fields=['used'])
        return redirect('accounts:login')

    return render(request, 'auth/reset_password.html', {'valid': True, 'form': form})
