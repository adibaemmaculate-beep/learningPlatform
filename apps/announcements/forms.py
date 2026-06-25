from django import forms

from apps.accounts.models import User

from .models import Announcement


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'body', 'visibility', 'target_student']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full border border-outline-variant rounded-lg px-3 py-2'}),
            'body': forms.Textarea(attrs={'rows': 6, 'class': 'w-full border border-outline-variant rounded-lg px-3 py-2'}),
            'visibility': forms.Select(attrs={'class': 'w-full border border-outline-variant rounded-lg px-3 py-2', 'id': 'id_visibility'}),
            'target_student': forms.Select(attrs={'class': 'w-full border border-outline-variant rounded-lg px-3 py-2', 'id': 'id_target_student'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['target_student'].queryset = User.objects.filter(
            type=User.UserType.STUDENT, status=User.UserStatus.ACTIVE
        ).order_by('first_name', 'last_name')
        self.fields['target_student'].required = False

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('visibility') == Announcement.Visibility.SPECIFIC_STUDENT and not cleaned.get('target_student'):
            raise forms.ValidationError('Select a student for targeted announcements.')
        return cleaned
