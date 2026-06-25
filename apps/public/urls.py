from django.urls import path

from . import views

app_name = 'public'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('students/', views.students, name='students'),
    path('students/<uuid:student_id>/', views.student_detail, name='student_detail'),
    path('contact/', views.contact, name='contact'),
]
