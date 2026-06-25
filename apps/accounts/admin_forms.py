from datetime import timedelta

from django import forms
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone

from apps.accounts.models import InviteCode, User
from apps.updates.models import Update


class GenerateInviteCodeForm(forms.Form):
    role = forms.ChoiceField(choices=InviteCode.Role.choices)
    expires_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        initial=timezone.now() + timedelta(days=30),
    )
    is_single_use = forms.BooleanField(initial=True, required=False)


class UserFilterForm(forms.Form):
    role = forms.ChoiceField(
        choices=[('', 'All roles')] + list(User.UserType.choices),
        required=False,
    )
    status = forms.ChoiceField(
        choices=[('', 'All statuses')] + list(User.UserStatus.choices),
        required=False,
    )
    q = forms.CharField(required=False, label='Search')


class CreateAdminForm(forms.Form):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') != cleaned.get('confirm_password'):
            raise forms.ValidationError('Passwords do not match.')
        if cleaned.get('password'):
            validate_password(cleaned['password'])
        return cleaned


class UpdateForm(forms.ModelForm):
    publish = forms.BooleanField(required=False, label='Publish now')

    class Meta:
        model = Update
        fields = ['title', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 8, 'class': 'w-full border border-outline-variant rounded-lg p-3'}),
            'title': forms.TextInput(attrs={'class': 'w-full border border-outline-variant rounded-lg p-3'}),
        }


class AdminSettingsForm(forms.Form):
    theme = forms.ChoiceField(choices=[('light', 'Light'), ('dark', 'Dark')])
    email_notifications = forms.BooleanField(required=False)
    current_password = forms.CharField(widget=forms.PasswordInput, required=False)
    new_password = forms.CharField(widget=forms.PasswordInput, required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=False)

    def clean(self):
        cleaned = super().clean()
        new = cleaned.get('new_password')
        confirm = cleaned.get('confirm_password')
        current = cleaned.get('current_password')
        if new or confirm or current:
            if not current:
                raise forms.ValidationError('Current password is required to change password.')
            if new != confirm:
                raise forms.ValidationError('New passwords do not match.')
            if new:
                validate_password(new)
        return cleaned
