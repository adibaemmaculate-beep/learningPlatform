import json

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.accounts.models import User
from apps.assignments.services import get_active_students
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
    return render(request, 'public/about.html', {
        'active_public_nav': 'about',
    })


def students(request):
    students_qs = (
        get_active_students()
        .select_related('profile', 'project')
        .order_by('first_name', 'last_name')
    )
    students_data = []
    for student in students_qs:
        profile = getattr(student, 'profile', None)
        project = None
        try:
            project = student.project
        except Project.DoesNotExist:
            pass
        profile_pic_url = None
        if profile and profile.profile_pic:
            profile_pic_url = profile.profile_pic.url
        project_url = None
        if project and project.is_published:
            project_url = reverse('public:student_detail', args=[student.id])
        students_data.append({
            'id': str(student.id),
            'name': student.get_full_name(),
            'bio': profile.bio if profile else '',
            'profile_pic_url': profile_pic_url,
            'initials': f'{student.first_name[:1]}{student.last_name[:1]}',
            'project_url': project_url,
        })
    return render(request, 'public/students.html', {
        'students': students_qs,
        'students_json': json.dumps(students_data),
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


def updates_list(request):
    published = Update.objects.filter(published_at__isnull=False).select_related('writer')
    paginator = Paginator(published, 9)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'public/updates.html', {
        'page_obj': page_obj,
        'updates': page_obj.object_list,
        'active_public_nav': 'updates',
    })


def update_detail(request, update_id):
    update = get_object_or_404(
        Update.objects.select_related('writer'),
        id=update_id,
        published_at__isnull=False,
    )
    related_updates = (
        Update.objects.filter(published_at__isnull=False)
        .exclude(id=update.id)
        .select_related('writer')[:3]
    )
    return render(request, 'public/update_detail.html', {
        'update': update,
        'related_updates': related_updates,
        'active_public_nav': 'updates',
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
