def portal_context(request):
    from apps.accounts.models import User

    user = request.user
    profile = None
    unread = []
    if user.is_authenticated:
        profile = getattr(user, 'profile', None)
        if user.type == User.UserType.STUDENT:
            from apps.announcements.services import unread_announcements
            unread = list(unread_announcements(user))
    return {
        'current_user_profile': profile,
        'portal_role': user.type if user.is_authenticated else None,
        'unread_announcements': unread,
    }
