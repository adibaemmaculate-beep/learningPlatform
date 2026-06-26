import os
import secrets
import string
import uuid as uuid_mod
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core.mail import send_mail
from apps.notifications.services import EmailNotificationService
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.accounts.admin_forms import (
    AdminSettingsForm,
    CreateAdminForm,
    GenerateInviteCodeForm,
    UpdateForm,
    UserFilterForm,
)
from apps.accounts.decorators import admin_required
from apps.accounts.models import InviteCode, PasswordResetToken, User
from apps.accounts.tokens import generate_token, get_reset_url
from apps.audit.models import AuditLog
from apps.audit.utils import log_action
from apps.profiles.models import Profile
from apps.assignments.models import Assignment, AssignmentSubmission
from apps.newsletter.models import Newsletter
from apps.updates.models import Update


def _generate_invite_code(role):
    prefix = 'STU' if role == InviteCode.Role.STUDENT else 'TCH'
    chars = string.ascii_uppercase + string.digits
    suffix = ''.join(secrets.choice(chars) for _ in range(4))
    year = timezone.now().year
    return f'ZW-{year}-{prefix}-{suffix}'


@admin_required
def admin_home(request):
    pending_users = User.objects.filter(status=User.UserStatus.PENDING).order_by('-created_at')
    recent_audit = AuditLog.objects.select_related('actor')[:10]
    stats = {
        'total_students': User.objects.filter(type=User.UserType.STUDENT, status=User.UserStatus.ACTIVE).count(),
        'total_teachers': User.objects.filter(type=User.UserType.TEACHER, status=User.UserStatus.ACTIVE).count(),
        'pending_approvals': pending_users.count(),
        'assignments_created': Assignment.objects.filter(is_draft=False).count(),
        'submissions_this_week': AssignmentSubmission.objects.filter(
            submitted_at__gte=timezone.now() - timedelta(days=7)
        ).count(),
        'newsletter_subscribers': Newsletter.objects.count(),
    }
    return render(request, 'admin/home.html', {
        'pending_users': pending_users,
        'recent_audit': recent_audit,
        'stats': stats,
        'active_nav': 'dashboard',
    })


@admin_required
@require_POST
def approve_user(request, user_id):
    user = get_object_or_404(User, id=user_id, status=User.UserStatus.PENDING)
    user.status = User.UserStatus.ACTIVE
    user.approved_at = timezone.now()
    user.approved_by = request.user
    user.save()
    Profile.objects.get_or_create(user=user)
    log_action(request.user, 'user_approved', 'user', user.id, {'email': user.email})
    EmailNotificationService.notify_account_approved(user)
    next_url = request.POST.get('next', 'admin_portal:home')
    if next_url.startswith('/'):
        return redirect(next_url)
    return redirect(next_url)


@admin_required
@require_POST
def reject_user(request, user_id):
    user = get_object_or_404(User, id=user_id, status=User.UserStatus.PENDING)
    email = user.email
    first_name = user.first_name
    user.delete()
    log_action(request.user, 'user_rejected', 'user', user_id, {'email': email})
    EmailNotificationService.notify_account_rejected_email(email, first_name)
    next_url = request.POST.get('next', 'admin_portal:home')
    if next_url.startswith('/'):
        return redirect(next_url)
    return redirect(next_url)


@admin_required
def users_list(request):
    form = UserFilterForm(request.GET or None)
    users = User.objects.select_related('profile').all()
    if form.is_valid():
        if form.cleaned_data.get('role'):
            users = users.filter(type=form.cleaned_data['role'])
        if form.cleaned_data.get('status'):
            users = users.filter(status=form.cleaned_data['status'])
        q = form.cleaned_data.get('q', '').strip()
        if q:
            users = users.filter(
                Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(email__icontains=q)
            )
    return render(request, 'admin/users.html', {
        'users': users,
        'filter_form': form,
        'active_nav': 'users',
    })


@admin_required
def user_detail(request, user_id):
    user = get_object_or_404(User.objects.select_related('profile'), id=user_id)
    return render(request, 'admin/user_detail.html', {
        'detail_user': user,
        'active_nav': 'users',
    })


@admin_required
def create_admin(request):
    form = CreateAdminForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        admin_user = User.objects.create_user(
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password'],
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            type=User.UserType.ADMIN,
            status=User.UserStatus.ACTIVE,
            email_verified=True,
            is_staff=True,
            is_superuser=True,
        )
        Profile.objects.get_or_create(user=admin_user)
        log_action(request.user, 'admin_created', 'user', admin_user.id, {'email': admin_user.email})
        messages.success(request, f'Admin account created for {admin_user.email}')
        return redirect('admin_portal:user_detail', user_id=admin_user.id)
    return render(request, 'admin/create_admin.html', {
        'form': form,
        'active_nav': 'users',
    })


@admin_required
@require_POST
def user_suspend(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.status = User.UserStatus.SUSPENDED
    user.save(update_fields=['status'])
    log_action(request.user, 'user_suspended', 'user', user.id, {'email': user.email})
    messages.success(request, f'{user.get_full_name()} has been suspended.')
    return redirect('admin_portal:user_detail', user_id=user.id)


@admin_required
@require_POST
def user_activate(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.status = User.UserStatus.ACTIVE
    user.save(update_fields=['status'])
    Profile.objects.get_or_create(user=user)
    log_action(request.user, 'user_activated', 'user', user.id, {'email': user.email})
    messages.success(request, f'{user.get_full_name()} has been activated.')
    return redirect('admin_portal:user_detail', user_id=user.id)


@admin_required
@require_POST
def user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.id == request.user.id:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('admin_portal:user_detail', user_id=user.id)
    email = user.email
    user.delete()
    log_action(request.user, 'user_deleted', 'user', user_id, {'email': email})
    messages.success(request, f'User {email} has been deleted.')
    return redirect('admin_portal:users')


@admin_required
@require_POST
def user_reset_password(request, user_id):
    user = get_object_or_404(User, id=user_id)
    token_str = generate_token()
    PasswordResetToken.objects.create(
        user=user,
        token=token_str,
        expires_at=timezone.now() + timedelta(hours=24),
    )
    reset_url = get_reset_url(request, token_str)
    send_mail(
        subject='Reset your password',
        message=f'An administrator requested a password reset. Visit: {reset_url}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
    log_action(request.user, 'password_reset_sent', 'user', user.id, {'email': user.email})
    messages.success(request, f'Password reset email sent to {user.email}')
    return redirect('admin_portal:user_detail', user_id=user.id)


@admin_required
def invite_codes_view(request):
    form = GenerateInviteCodeForm(request.POST or None)
    created_code = None
    if request.method == 'POST' and form.is_valid():
        code_str = _generate_invite_code(form.cleaned_data['role'])
        invite = InviteCode.objects.create(
            code=code_str,
            role=form.cleaned_data['role'],
            created_by=request.user,
            expires_at=form.cleaned_data['expires_at'],
            is_single_use=form.cleaned_data['is_single_use'],
        )
        log_action(request.user, 'invite_code_generated', 'invite_code', invite.id, {'code': code_str})
        created_code = code_str
        form = GenerateInviteCodeForm()
        messages.success(request, f'Invite code created: {created_code}')

    invite_codes = InviteCode.objects.select_related('used_by', 'created_by').all()
    return render(request, 'admin/invite_codes.html', {
        'form': form,
        'created_code': created_code,
        'invite_codes': invite_codes,
        'active_nav': 'invite_codes',
    })


@admin_required
@require_POST
def deactivate_invite_code(request, code_id):
    invite = get_object_or_404(InviteCode, id=code_id)
    if invite.status == InviteCode.Status.ACTIVE:
        invite.status = InviteCode.Status.EXPIRED
        invite.save(update_fields=['status'])
        log_action(request.user, 'invite_code_deactivated', 'invite_code', invite.id, {'code': invite.code})
        messages.success(request, f'Code {invite.code} deactivated.')
    return redirect('admin_portal:invite_codes')


@admin_required
def updates_list(request):
    updates = Update.objects.select_related('writer').all()
    return render(request, 'admin/updates.html', {
        'updates': updates,
        'active_nav': 'updates',
    })


@admin_required
def update_create(request):
    form = UpdateForm(
        request.POST or None,
        request.FILES or None,
        initial={'author_name': request.user.get_full_name()},
    )
    if request.method == 'POST' and form.is_valid():
        update = form.save(commit=False)
        update.writer = request.user
        if form.cleaned_data.get('publish'):
            update.published_at = timezone.now()
        update.save()
        log_action(request.user, 'update_created', 'update', update.id, {'title': update.title})
        messages.success(request, 'Update saved.')
        return redirect('admin_portal:updates')
    return render(request, 'admin/update_form.html', {
        'form': form,
        'active_nav': 'updates',
        'editing': False,
    })


@admin_required
def update_edit(request, update_id):
    update = get_object_or_404(Update, id=update_id)
    form = UpdateForm(request.POST or None, request.FILES or None, instance=update)
    if request.method == 'POST' and form.is_valid():
        update = form.save(commit=False)
        if form.cleaned_data.get('publish') and not update.published_at:
            update.published_at = timezone.now()
        update.save()
        log_action(request.user, 'update_edited', 'update', update.id, {'title': update.title})
        messages.success(request, 'Update saved.')
        return redirect('admin_portal:updates')
    return render(request, 'admin/update_form.html', {
        'form': form,
        'update_obj': update,
        'active_nav': 'updates',
        'editing': True,
    })


@admin_required
@require_POST
def update_image_upload(request):
    file_obj = request.FILES.get('image')
    if not file_obj:
        return JsonResponse({'error': 'No image provided.'}, status=400)
    ext = os.path.splitext(file_obj.name)[1].lower()
    if ext not in {'.jpg', '.jpeg', '.png', '.webp'}:
        return JsonResponse({'error': 'Invalid file type. Use JPG, PNG, or WebP.'}, status=400)
    if file_obj.size > 5 * 1024 * 1024:
        return JsonResponse({'error': 'Image must be under 5 MB.'}, status=400)
    path = f'updates/inline/{uuid_mod.uuid4().hex}{ext}'
    saved = default_storage.save(path, file_obj)
    return JsonResponse({'url': default_storage.url(saved)})


@admin_required
@require_POST
def update_delete(request, update_id):
    update = get_object_or_404(Update, id=update_id)
    title = update.title
    update.delete()
    log_action(request.user, 'update_deleted', 'update', update_id, {'title': title})
    messages.success(request, f'Update "{title}" deleted.')
    return redirect('admin_portal:updates')


@admin_required
def newsletter_subscribers(request):
    q = request.GET.get('q', '').strip()
    subscribers = Newsletter.objects.all()
    if q:
        subscribers = subscribers.filter(email__icontains=q)
    return render(request, 'admin/newsletter.html', {
        'subscribers': subscribers,
        'search_query': q,
        'total_count': Newsletter.objects.count(),
        'active_nav': 'newsletter',
    })


@admin_required
def settings_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    initial = {
        'theme': profile.theme,
        'email_notifications': profile.email_notifications,
    }
    form = AdminSettingsForm(request.POST or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        new_password = form.cleaned_data.get('new_password')
        if new_password and not request.user.check_password(form.cleaned_data['current_password']):
            form.add_error('current_password', 'Current password is incorrect.')
        else:
            profile.theme = form.cleaned_data['theme']
            profile.email_notifications = form.cleaned_data['email_notifications']
            profile.save()
            if new_password:
                request.user.set_password(new_password)
                request.user.save()
                log_action(request.user, 'password_changed', 'user', request.user.id, {})
                messages.success(request, 'Password updated successfully.')
                return redirect('accounts:login')
            log_action(request.user, 'settings_updated', 'user', request.user.id, {})
            messages.success(request, 'Settings saved.')
            return redirect('admin_portal:settings')
    return render(request, 'shared/settings.html', {
        'form': form,
        'active_nav': 'settings',
        'portal_role': 'admin',
    })
