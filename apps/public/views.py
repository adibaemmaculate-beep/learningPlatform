from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.models import User
from apps.newsletter.models import Newsletter
from apps.projects.models import Project
from apps.updates.models import Update

from .forms import ContactForm, NewsletterSignupForm


def home(request):
    if request.method == 'POST' and request.POST.get('form_type') == 'newsletter':
        form = NewsletterSignupForm(request.POST)
        if form.is_valid():
            Newsletter.objects.create(email=form.cleaned_data['email'])
            messages.success(request, 'Thanks for subscribing to our newsletter!')
            return redirect('public:home')
        return render(request, 'public/home.html', {
            'latest_updates': Update.objects.filter(published_at__isnull=False)[:3],
            'newsletter_form': form,
            'active_public_nav': 'home',
        })

    latest_updates = Update.objects.filter(published_at__isnull=False).select_related('writer')[:3]
    return render(request, 'public/home.html', {
        'latest_updates': latest_updates,
        'newsletter_form': NewsletterSignupForm(),
        'active_public_nav': 'home',
    })


def about(request):
    teachers = User.objects.filter(
        type=User.UserType.TEACHER, status=User.UserStatus.ACTIVE
    ).select_related('profile')[:6]
    return render(request, 'public/about.html', {
        'teachers': teachers,
        'active_public_nav': 'about',
    })


def students(request):
    published_projects = Project.objects.filter(
        is_published=True,
        student__status=User.UserStatus.ACTIVE,
    ).select_related('student', 'student__profile').prefetch_related('images')
    return render(request, 'public/students.html', {
        'projects': published_projects,
        'active_public_nav': 'students',
    })


def student_detail(request, student_id):
    student = get_object_or_404(User, id=student_id, type=User.UserType.STUDENT, status=User.UserStatus.ACTIVE)
    project = None
    try:
        proj = student.project
        if proj.is_published:
            project = proj
    except Project.DoesNotExist:
        pass
    if not project:
        from django.http import Http404
        raise Http404('Published project not found.')
    return render(request, 'public/student_detail.html', {
        'student': student,
        'project': project,
        'active_public_nav': 'students',
    })


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            send_mail(
                subject=f'Contact form: {form.cleaned_data["name"]}',
                message=(
                    f'From: {form.cleaned_data["name"]} <{form.cleaned_data["email"]}>\n\n'
                    f'{form.cleaned_data["message"]}'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=False,
            )
            messages.success(request, 'Your message has been sent. We will get back to you soon.')
            return redirect('public:contact')
    else:
        form = ContactForm()
    return render(request, 'public/contact.html', {
        'form': form,
        'active_public_nav': 'contact',
    })
