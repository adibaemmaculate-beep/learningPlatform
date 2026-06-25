from django import forms

from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'write_up', 'codebase_url', 'live_url', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full border border-outline-variant rounded-lg px-3 py-2'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'w-full border border-outline-variant rounded-lg px-3 py-2'}),
            'write_up': forms.Textarea(attrs={'rows': 8, 'class': 'w-full border border-outline-variant rounded-lg px-3 py-2', 'placeholder': 'Markdown supported...'}),
            'codebase_url': forms.URLInput(attrs={'class': 'w-full border border-outline-variant rounded-lg px-3 py-2', 'placeholder': 'https://github.com/...'}),
            'live_url': forms.URLInput(attrs={'class': 'w-full border border-outline-variant rounded-lg px-3 py-2', 'placeholder': 'https://...'}),
        }
