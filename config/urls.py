from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from apps.accounts import admin_portal_views, portal_views
from apps.announcements import views as announcement_views
from apps.assignments import views as assignment_views
from apps.courses import views as course_views
from apps.profiles import views as profile_views
from apps.projects import views as project_views

admin_panel_patterns = ([
    path('', admin_portal_views.admin_home, name='home'),
    path('approve/<uuid:user_id>/', admin_portal_views.approve_user, name='approve_user'),
    path('reject/<uuid:user_id>/', admin_portal_views.reject_user, name='reject_user'),
    path('users/', admin_portal_views.users_list, name='users'),
    path('users/create-admin/', admin_portal_views.create_admin, name='create_admin'),
    path('users/<uuid:user_id>/', admin_portal_views.user_detail, name='user_detail'),
    path('users/<uuid:user_id>/suspend/', admin_portal_views.user_suspend, name='user_suspend'),
    path('users/<uuid:user_id>/activate/', admin_portal_views.user_activate, name='user_activate'),
    path('users/<uuid:user_id>/delete/', admin_portal_views.user_delete, name='user_delete'),
    path('users/<uuid:user_id>/reset-password/', admin_portal_views.user_reset_password, name='user_reset_password'),
    path('invite-codes/', admin_portal_views.invite_codes_view, name='invite_codes'),
    path('invite-codes/<uuid:code_id>/deactivate/', admin_portal_views.deactivate_invite_code, name='deactivate_invite_code'),
    path('updates/', admin_portal_views.updates_list, name='updates'),
    path('updates/create/', admin_portal_views.update_create, name='update_create'),
    path('updates/<uuid:update_id>/edit/', admin_portal_views.update_edit, name='update_edit'),
    path('updates/<uuid:update_id>/delete/', admin_portal_views.update_delete, name='update_delete'),
    path('settings/', admin_portal_views.settings_view, name='settings'),
], 'admin_portal')

student_patterns = ([
    path('', portal_views.student_home, name='home'),
    path('assignments/', assignment_views.student_assignments, name='assignments'),
    path('assignments/<uuid:assignment_id>/', assignment_views.student_assignment_detail, name='assignment_detail'),
    path('grades/', assignment_views.student_grades, name='grades'),
    path('project/', project_views.student_project, name='project'),
    path('announcements/', announcement_views.student_announcements, name='announcements'),
    path('announcements/<uuid:announcement_id>/', announcement_views.student_announcement_detail, name='announcement_detail'),
    path('materials/', course_views.student_materials, name='materials'),
    path('profile/', profile_views.student_profile, name='profile'),
    path('settings/', profile_views.student_settings, name='settings'),
], 'student')

teacher_patterns = ([
    path('', portal_views.teacher_home, name='home'),
    path('assignments/', assignment_views.teacher_assignments, name='assignments'),
    path('assignments/create/', assignment_views.teacher_assignment_create, name='assignment_create'),
    path('assignments/<uuid:assignment_id>/', assignment_views.teacher_assignment_detail, name='assignment_detail'),
    path('assignments/<uuid:assignment_id>/edit/', assignment_views.teacher_assignment_edit, name='assignment_edit'),
    path('assignments/<uuid:assignment_id>/delete/', assignment_views.teacher_assignment_delete, name='assignment_delete'),
    path('assignments/<uuid:assignment_id>/release-grades/', assignment_views.teacher_release_grades, name='release_grades'),
    path('assignments/<uuid:assignment_id>/grade/<uuid:submission_id>/', assignment_views.teacher_grade_submission, name='grade_submission'),
    path('students/', assignment_views.teacher_students, name='students'),
    path('students/<uuid:student_id>/', assignment_views.teacher_student_detail, name='student_detail'),
    path('progress/', assignment_views.teacher_progress, name='progress'),
    path('projects/', project_views.teacher_projects, name='projects'),
    path('projects/<uuid:project_id>/', project_views.teacher_project_detail, name='project_detail'),
    path('announcements/', announcement_views.announcements_list, name='announcements'),
    path('announcements/create/', announcement_views.announcement_create, name='announcement_create'),
    path('announcements/<uuid:announcement_id>/', announcement_views.announcement_detail, name='announcement_detail'),
    path('materials/', course_views.teacher_materials, name='materials'),
    path('materials/create/', course_views.material_create, name='material_create'),
    path('materials/<uuid:material_id>/edit/', course_views.material_edit, name='material_edit'),
    path('materials/<uuid:material_id>/delete/', course_views.material_delete, name='material_delete'),
    path('materials/<uuid:material_id>/toggle-publish/', course_views.material_toggle_publish, name='material_toggle_publish'),
    path('profile/', profile_views.teacher_profile, name='profile'),
    path('settings/', profile_views.teacher_settings, name='settings'),
], 'teacher')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('apps.accounts.urls')),
    path('admin-panel/', include(admin_panel_patterns, namespace='admin_portal')),
    path('student/', include(student_patterns, namespace='student')),
    path('teacher/', include(teacher_patterns, namespace='teacher')),
    path('', include('apps.public.urls')),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
