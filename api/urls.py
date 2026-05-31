from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_user, name='login'),
    path('applications/', views.application, name='applications'),
    path('admin_applications/', views.admin_applications, name='admin_applications'),
]