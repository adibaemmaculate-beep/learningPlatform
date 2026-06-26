import os

from django import forms

from .models import Project

MAX_WRITE_UP_BYTES = 10 * 1024 * 1024


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'write_up', 'codebase_url', 'live_url', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full border border-outline-variant rounded-lg px-3 py-2'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'w-full border border-outline-variant rounded-lg px-3 py-2'}),
            'write_up': forms.FileInput(attrs={
                'class': 'text-body-sm',
                'accept': '.pdf,application/pdf',
            }),
            'codebase_url': forms.URLInput(attrs={'class': 'w-full border border-outline-variant rounded-lg px-3 py-2', 'placeholder': 'https://github.com/...'}),
            'live_url': forms.URLInput(attrs={'class': 'w-full border border-outline-variant rounded-lg px-3 py-2', 'placeholder': 'https://...'}),
        }

    def clean_write_up(self):
        write_up = self.cleaned_data.get('write_up')
        if not write_up:
            return write_up
        ext = os.path.splitext(write_up.name)[1].lower()
        if ext != '.pdf':
            raise forms.ValidationError('Write-up must be a PDF file.')
        if write_up.size > MAX_WRITE_UP_BYTES:
            raise forms.ValidationError('Write-up must be under 10 MB.')
        return write_up
