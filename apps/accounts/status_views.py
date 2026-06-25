from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def pending_approval_view(request):
    return render(request, 'auth/pending_approval.html')


@login_required
def suspended_view(request):
    return render(request, 'auth/suspended.html')


@login_required
def verify_required_view(request):
    return render(request, 'auth/verify_required.html')
