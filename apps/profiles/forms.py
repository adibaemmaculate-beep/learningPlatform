import os

from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from config.form_widgets import MARKDOWN_TEXTAREA_ATTRS

from apps.accounts.models import User
from apps.profiles.models import Profile

PROFILE_PIC_MAX_BYTES = 10 * 1024 * 1024
PROFILE_PIC_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
PROFILE_PIC_ACCEPT = '.jpg,.jpeg,.png,.webp'
PROFILE_PIC_HELP_TEXT = 'JPG, PNG, or WebP. Max 10 MB.'


def validate_profile_pic(file_obj):
    if not file_obj or not hasattr(file_obj, 'size'):
        return file_obj
    ext = os.path.splitext(file_obj.name)[1].lower()
    if ext not in PROFILE_PIC_EXTENSIONS:
        raise ValidationError('Profile picture must be JPG, PNG, or WebP.')
    if file_obj.size > PROFILE_PIC_MAX_BYTES:
        raise ValidationError('Profile picture must be under 10 MB.')
    return file_obj


class UserNameForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full border border-outline-variant rounded-lg px-3 py-2',
                'required': True,
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full border border-outline-variant rounded-lg px-3 py-2',
                'required': True,
            }),
        }

    def clean_first_name(self):
        value = (self.cleaned_data.get('first_name') or '').strip()
        if not value:
            raise ValidationError('First name is required.')
        return value

    def clean_last_name(self):
        value = (self.cleaned_data.get('last_name') or '').strip()
        if not value:
            raise ValidationError('Last name is required.')
        return value


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'profile_pic']
        widgets = {
            'bio': forms.Textarea(attrs={
                **MARKDOWN_TEXTAREA_ATTRS,
                'placeholder': 'Tell your story...',
            }),
            'profile_pic': forms.FileInput(attrs={
                'accept': PROFILE_PIC_ACCEPT,
                'class': 'text-body-sm',
            }),
        }

    def clean_profile_pic(self):
        return validate_profile_pic(self.cleaned_data.get('profile_pic'))


class PortalSettingsForm(forms.Form):
    theme = forms.ChoiceField(choices=Profile.Theme.choices)
    email_notifications = forms.BooleanField(required=False)
    phone_number = forms.CharField(max_length=30, required=False, label='Phone number')
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
                raise ValidationError('Current password is required to change password.')
            if new != confirm:
                raise ValidationError('New passwords do not match.')
            if new:
                validate_password(new)
        return cleaned
