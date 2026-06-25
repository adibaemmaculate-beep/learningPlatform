from django.conf import settings
from django.shortcuts import redirect
from django.urls import resolve


class RoleRedirectMiddleware:
    """Protect portal routes and redirect users based on role."""

    PUBLIC_PREFIXES = ('/auth/', '/static/', '/uploads/', '/admin/')
    PUBLIC_EXACT = ('/', '/about/', '/students/', '/contact/')

    PORTAL_PREFIXES = {
        '/student/': 'student',
        '/teacher/': 'teacher',
        '/admin-panel/': 'admin',
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        if any(path.startswith(p) for p in self.PUBLIC_PREFIXES):
            return self.get_response(request)

        if path in self.PUBLIC_EXACT or path.startswith('/students/'):
            return self.get_response(request)

        for prefix, required_role in self.PORTAL_PREFIXES.items():
            if path.startswith(prefix):
                if not request.user.is_authenticated:
                    return redirect(settings.LOGIN_URL)
                if request.user.status == 'pending':
                    return redirect('accounts:pending_approval')
                if request.user.status == 'suspended':
                    return redirect('accounts:suspended')
                if settings.REQUIRE_EMAIL_VERIFICATION and not request.user.email_verified:
                    return redirect('accounts:verify_required')
                if request.user.type != required_role:
                    return redirect(request.user.get_portal_home_url())
                break

        return self.get_response(request)
