from django import forms

from apps.newsletter.models import Newsletter


class NewsletterSignupForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if Newsletter.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already subscribed.')
        return email


class ContactForm(forms.Form):
    name = forms.CharField(max_length=150)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}))
