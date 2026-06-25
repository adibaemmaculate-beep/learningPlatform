from django.urls import path

from . import status_views, views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('verify/<str:token>/', views.verify_email_view, name='verify_email'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset/<str:token>/', views.reset_password_view, name='reset_password'),
    path('pending/', status_views.pending_approval_view, name='pending_approval'),
    path('suspended/', status_views.suspended_view, name='suspended'),
    path('verify-required/', status_views.verify_required_view, name='verify_required'),
]
