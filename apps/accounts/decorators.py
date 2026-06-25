from functools import wraps

from django.shortcuts import redirect

from apps.accounts.models import User


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if request.user.type != User.UserType.ADMIN:
            return redirect(request.user.get_portal_home_url())
        return view_func(request, *args, **kwargs)
    return wrapper
