from django import forms
from django.core.exceptions import ValidationError

from apps.courses.models import CourseMaterial
from config.form_widgets import MARKDOWN_TEXTAREA_ATTRS


def get_active_course():
    from apps.courses.models import Course
    return Course.objects.filter(is_active=True).first()


class CourseMaterialForm(forms.ModelForm):
    objectives_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'One objective per line'}),
        label='Learning objectives',
    )
    other_resources_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'label|url per line'}),
        label='Other resources',
    )
    publish = forms.BooleanField(required=False, label='Publish (visible to students)')

    class Meta:
        model = CourseMaterial
        fields = ['week', 'title', 'description', 'slides', 'notes']
        widgets = {
            'week': forms.NumberInput(attrs={'class': 'w-full border border-outline-variant rounded-lg px-3 py-2', 'min': 1}),
            'title': forms.TextInput(attrs={'class': 'w-full border border-outline-variant rounded-lg px-3 py-2'}),
            'description': forms.Textarea(attrs=MARKDOWN_TEXTAREA_ATTRS),
            'slides': forms.ClearableFileInput(attrs={'accept': '.pdf', 'class': 'w-full text-body-sm'}),
            'notes': forms.ClearableFileInput(attrs={'accept': '.pdf', 'class': 'w-full text-body-sm'}),
        }

    def __init__(self, *args, **kwargs):
        self.course = kwargs.pop('course', None)
        super().__init__(*args, **kwargs)
        if self.course is None and self.instance and self.instance.pk:
            self.course = self.instance.course
        if self.instance and self.instance.pk:
            self.fields['objectives_text'].initial = '\n'.join(self.instance.objectives_json or [])
            resources = self.instance.other_resources_json or []
            self.fields['other_resources_text'].initial = '\n'.join(
                f'{r.get("label", "")}|{r.get("url", "")}' for r in resources
            )
            self.fields['publish'].initial = self.instance.published

    def clean_week(self):
        week = self.cleaned_data.get('week')
        if week is not None and self.course is not None:
            qs = CourseMaterial.objects.filter(course=self.course, week=week)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError(f'Week {week} already has materials for this course.')
        return week

    def clean_slides(self):
        return self._validate_pdf(self.cleaned_data.get('slides'))

    def clean_notes(self):
        return self._validate_pdf(self.cleaned_data.get('notes'))

    def _validate_pdf(self, file_obj):
        if not file_obj:
            return file_obj
        if not file_obj.name.lower().endswith('.pdf'):
            raise ValidationError('Only PDF files are allowed.')
        if file_obj.size > 20 * 1024 * 1024:
            raise ValidationError('File must be under 20 MB.')
        return file_obj

    def clean(self):
        cleaned = super().clean()
        objectives_text = cleaned.get('objectives_text', '')
        cleaned['objectives_list'] = [
            line.strip() for line in objectives_text.splitlines() if line.strip()
        ]
        resources = []
        for line in cleaned.get('other_resources_text', '').splitlines():
            line = line.strip()
            if not line:
                continue
            if '|' not in line:
                raise ValidationError({'other_resources_text': 'Each resource must be: label|url'})
            label, url = line.split('|', 1)
            resources.append({'label': label.strip(), 'url': url.strip()})
        cleaned['resources_list'] = resources
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.objectives_json = self.cleaned_data.get('objectives_list', [])
        instance.other_resources_json = self.cleaned_data.get('resources_list', [])
        instance.published = self.cleaned_data.get('publish', False)
        if commit:
            instance.save()
        return instance
