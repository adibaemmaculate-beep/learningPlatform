import os

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.courses.forms import get_active_course
from config.form_widgets import MARKDOWN_TEXTAREA_ATTRS

from .models import Assignment, AssignmentSubmission

FILE_TYPE_CHOICES = [
    ('.pdf', 'PDF (.pdf)'),
    ('.py', 'Python (.py)'),
    ('.zip', 'ZIP (.zip)'),
    ('.ipynb', 'Jupyter (.ipynb)'),
    ('.docx', 'Word (.docx)'),
    ('.mp4', 'Video (.mp4)'),
]


class AssignmentForm(forms.ModelForm):
    allowed_types = forms.MultipleChoiceField(
        choices=FILE_TYPE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label='Allowed file types',
    )
    publish = forms.BooleanField(required=False, label='Publish (visible to students)')

    class Meta:
        model = Assignment
        fields = ['title', 'week', 'due_date', 'instructions', 'total_score', 'max_file_size_mb']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full border border-outline-variant rounded-lg px-3 py-2'}),
            'week': forms.NumberInput(attrs={'class': 'w-full border border-outline-variant rounded-lg px-3 py-2', 'min': 1}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'w-full border border-outline-variant rounded-lg px-3 py-2'}),
            'instructions': forms.Textarea(attrs=MARKDOWN_TEXTAREA_ATTRS),
            'total_score': forms.NumberInput(attrs={'class': 'w-full border border-outline-variant rounded-lg px-3 py-2', 'min': 1}),
            'max_file_size_mb': forms.NumberInput(attrs={'class': 'w-full border border-outline-variant rounded-lg px-3 py-2', 'min': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['allowed_types'].initial = self.instance.allowed_file_types or []
            self.fields['publish'].initial = not self.instance.is_draft

    def save(self, commit=True, created_by=None):
        instance = super().save(commit=False)
        instance.allowed_file_types = self.cleaned_data['allowed_types']
        instance.is_draft = not self.cleaned_data.get('publish', False)
        if created_by:
            instance.created_by = created_by
        course = get_active_course()
        if course:
            instance.course = course
        if commit:
            instance.save()
        return instance


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['file']

    def __init__(self, *args, assignment=None, **kwargs):
        self.assignment = assignment
        super().__init__(*args, **kwargs)
        self.fields['file'].widget.attrs.update({
            'class': 'w-full text-body-sm',
            'data-file-upload': 'true',
        })
        if assignment and assignment.allowed_file_types:
            self.fields['file'].widget.attrs['accept'] = ','.join(assignment.allowed_file_types)
            self.fields['file'].widget.attrs['data-allowed-types'] = ','.join(assignment.allowed_file_types)
            self.fields['file'].widget.attrs['data-max-size-mb'] = str(assignment.max_file_size_mb)

    def clean_file(self):
        file_obj = self.cleaned_data.get('file')
        if not file_obj or not self.assignment:
            return file_obj
        ext = os.path.splitext(file_obj.name)[1].lower()
        allowed = [t.lower() for t in self.assignment.allowed_file_types]
        if ext not in allowed:
            raise ValidationError(f'File type {ext} not allowed. Accepted: {", ".join(allowed)}')
        max_bytes = self.assignment.max_file_size_mb * 1024 * 1024
        if file_obj.size > max_bytes:
            raise ValidationError(f'File must be under {self.assignment.max_file_size_mb} MB.')
        return file_obj


class GradeSubmissionForm(forms.Form):
    score_obtained = forms.IntegerField(min_value=0)
    comments = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs=MARKDOWN_TEXTAREA_ATTRS),
    )

    def __init__(self, *args, max_score=100, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_score = max_score
        self.fields['score_obtained'].widget.attrs['max'] = max_score

    def clean_score_obtained(self):
        score = self.cleaned_data['score_obtained']
        if score > self.max_score:
            raise ValidationError(f'Score cannot exceed {self.max_score}.')
        return score
