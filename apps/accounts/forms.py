from django import forms
from django.utils import timezone

from .models import InviteCode, User


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'peer input-glow block w-full px-md pt-5 pb-2 text-on-surface bg-surface-container-lowest border border-outline-variant rounded appearance-none focus:outline-none transition-colors duration-200',
        'placeholder': ' ',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'peer input-glow block w-full px-md pt-5 pb-2 text-on-surface bg-surface-container-lowest border border-outline-variant rounded appearance-none focus:outline-none transition-colors duration-200',
        'placeholder': ' ',
    }))


class RegisterForm(forms.Form):
    invite_code = forms.CharField(max_length=50, label='Invite Code')
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=30, required=False)
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')

    def clean_invite_code(self):
        code = self.cleaned_data['invite_code'].strip().upper()
        try:
            invite = InviteCode.objects.get(code__iexact=code)
        except InviteCode.DoesNotExist:
            raise forms.ValidationError('Invalid invite code.')
        if not invite.is_valid():
            if timezone.now() > invite.expires_at:
                invite.status = InviteCode.Status.EXPIRED
                invite.save(update_fields=['status'])
            raise forms.ValidationError('This invite code is no longer valid.')
        self.cleaned_data['invite'] = invite
        return code

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') != cleaned.get('confirm_password'):
            raise forms.ValidationError('Passwords do not match.')
        return cleaned


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField()


class ResetPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') != cleaned.get('confirm_password'):
            raise forms.ValidationError('Passwords do not match.')
        return cleaned
