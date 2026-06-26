import os

from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from config.form_widgets import MARKDOWN_TEXTAREA_ATTRS

from apps.profiles.models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'profile_pic']
        widgets = {
            'bio': forms.Textarea(attrs={
                **MARKDOWN_TEXTAREA_ATTRS,
                'placeholder': 'Tell your story...',
            }),
        }

    def clean_profile_pic(self):
        file_obj = self.cleaned_data.get('profile_pic')
        if file_obj and hasattr(file_obj, 'size'):
            valid_ext = {'.jpg', '.jpeg', '.png', '.webp'}
            ext = os.path.splitext(file_obj.name)[1].lower()
            if ext not in valid_ext:
                raise ValidationError('Profile picture must be JPG, PNG, or WebP.')
            if file_obj.size > 2 * 1024 * 1024:
                raise ValidationError('Profile picture must be under 2 MB.')
        return file_obj


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
