from django.urls import path
from .import views

urlpatterns = [
    path('', views.login_request),
    path('login', views.login_request, name = 'login'),
    path('logout', views.logout_request, name = 'logout'),
    path('register', views.register, name = 'register'),
    path('input_email', views.input_email, name = 'input_email'),
    path('email_verification', views.email_verification, name = 'email_verification'),
    path('resend_code', views.resend_code, name = 'resend_code'),
    path('change_password_email', views.change_password_email, name = 'change_password_email'),
    path('profile', views.profile, name = 'profile'),
    path('change_password', views.change_password, name = 'change_password'),
]