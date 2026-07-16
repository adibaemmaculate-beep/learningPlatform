import os
from datetime import timedelta

from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import InviteCode, User
from apps.profiles.forms import (
    PROFILE_PIC_ACCEPT,
    PROFILE_PIC_HELP_TEXT,
    validate_profile_pic,
)
from apps.updates.models import Update
from config.form_widgets import MARKDOWN_TEXTAREA_ATTRS


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


class StudentProfileEditForm(forms.Form):
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'w-full border border-outline-variant rounded-lg px-3 py-2',
        }),
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'w-full border border-outline-variant rounded-lg px-3 py-2',
        }),
    )
    profile_pic = forms.ImageField(
        required=False,
        help_text=PROFILE_PIC_HELP_TEXT,
        widget=forms.FileInput(attrs={
            'accept': PROFILE_PIC_ACCEPT,
            'class': 'text-body-sm',
        }),
    )

    def __init__(self, *args, user=None, profile=None, **kwargs):
        self.user = user
        self.profile = profile
        super().__init__(*args, **kwargs)
        if user is not None and not self.is_bound:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name

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

    def clean_profile_pic(self):
        return validate_profile_pic(self.cleaned_data.get('profile_pic'))

    def save(self):
        if self.user is None or self.profile is None:
            raise ValueError('StudentProfileEditForm requires user and profile instances.')
        with transaction.atomic():
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            self.user.save(update_fields=['first_name', 'last_name'])
            uploaded = self.cleaned_data.get('profile_pic')
            if uploaded:
                if self.profile.profile_pic:
                    self.profile.profile_pic.delete(save=False)
                self.profile.profile_pic = uploaded
                self.profile.save()
        return self.user


class UpdateForm(forms.ModelForm):
    publish = forms.BooleanField(required=False, label='Publish now')
    remove_cover_image = forms.BooleanField(required=False, label='Remove cover image')

    class Meta:
        model = Update
        fields = ['title', 'author_name', 'description', 'cover_image', 'cover_image_caption']
        widgets = {
            'description': forms.Textarea(attrs=MARKDOWN_TEXTAREA_ATTRS),
            'title': forms.TextInput(attrs={'class': 'w-full border border-outline-variant rounded-lg p-3'}),
            'author_name': forms.TextInput(attrs={
                'class': 'w-full border border-outline-variant rounded-lg p-3',
                'placeholder': 'e.g. Jane Doe',
            }),
            'cover_image_caption': forms.TextInput(attrs={
                'class': 'w-full border border-outline-variant rounded-lg p-3',
                'placeholder': 'Describe the cover image (optional)',
            }),
            'cover_image': forms.FileInput(attrs={
                'accept': '.jpg,.jpeg,.png,.webp',
                'class': 'hidden',
                'id': 'id_cover_image',
            }),
        }

    def clean_cover_image(self):
        file_obj = self.cleaned_data.get('cover_image')
        if file_obj and hasattr(file_obj, 'size'):
            ext = os.path.splitext(file_obj.name)[1].lower()
            if ext not in {'.jpg', '.jpeg', '.png', '.webp'}:
                raise ValidationError('Cover image must be JPG, PNG, or WebP.')
            if file_obj.size > 5 * 1024 * 1024:
                raise ValidationError('Cover image must be under 5 MB.')
        return file_obj

    def save(self, commit=True):
        if self.instance.pk:
            try:
                old = Update.objects.get(pk=self.instance.pk)
                old_cover = old.cover_image
            except Update.DoesNotExist:
                old_cover = None
        else:
            old_cover = None

        instance = super().save(commit=False)
        if self.cleaned_data.get('remove_cover_image'):
            if instance.cover_image:
                instance.cover_image.delete(save=False)
            instance.cover_image = None
        elif old_cover and instance.cover_image and old_cover.name != instance.cover_image.name:
            old_cover.delete(save=False)

        if commit:
            instance.save()
        return instance


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
