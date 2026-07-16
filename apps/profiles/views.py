from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect, render

from apps.accounts.portal_decorators import student_required, teacher_required
from apps.audit.utils import log_action

from .forms import PortalSettingsForm, ProfileForm, UserNameForm
from .models import Profile


def _get_profile(user):
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile


@student_required
def student_profile(request):
    profile = _get_profile(request.user)
    name_form = UserNameForm(request.POST or None, instance=request.user)
    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)
    if request.method == 'POST' and name_form.is_valid() and form.is_valid():
        with transaction.atomic():
            name_form.save()
            form.save()
        log_action(request.user, 'profile_updated', 'profile', profile.id, {})
        messages.success(request, 'Profile updated.')
        return redirect('student:profile')
    return render(request, 'student/profile.html', {
        'form': form,
        'name_form': name_form,
        'profile': profile,
        'active_nav': 'profile',
    })


@teacher_required
def teacher_profile(request):
    profile = _get_profile(request.user)
    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)
    if request.method == 'POST' and form.is_valid():
        form.save()
        log_action(request.user, 'profile_updated', 'profile', profile.id, {})
        messages.success(request, 'Profile updated.')
        return redirect('teacher:profile')
    return render(request, 'teacher/profile.html', {
        'form': form,
        'profile': profile,
        'active_nav': 'profile',
    })


def _settings_view(request, redirect_name):
    profile = _get_profile(request.user)
    initial = {
        'theme': profile.theme,
        'email_notifications': profile.email_notifications,
        'phone_number': request.user.phone_number,
    }
    form = PortalSettingsForm(request.POST or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        new_password = form.cleaned_data.get('new_password')
        if new_password and not request.user.check_password(form.cleaned_data['current_password']):
            form.add_error('current_password', 'Current password is incorrect.')
        else:
            profile.theme = form.cleaned_data['theme']
            profile.email_notifications = form.cleaned_data['email_notifications']
            profile.save()
            request.user.phone_number = form.cleaned_data.get('phone_number', '')
            request.user.save(update_fields=['phone_number'])
            if new_password:
                request.user.set_password(new_password)
                request.user.save()
                log_action(request.user, 'password_changed', 'user', request.user.id, {})
                messages.success(request, 'Password updated. Please log in again.')
                return redirect('accounts:login')
            log_action(request.user, 'settings_updated', 'user', request.user.id, {})
            messages.success(request, 'Settings saved.')
            return redirect(redirect_name)
    portal_role = request.user.type
    return render(request, 'shared/settings.html', {
        'form': form,
        'profile': profile,
        'active_nav': 'settings',
        'portal_role': portal_role,
        'settings_redirect': redirect_name,
    })


@student_required
def student_settings(request):
    return _settings_view(request, 'student:settings')


@teacher_required
def teacher_settings(request):
    return _settings_view(request, 'teacher:settings')
