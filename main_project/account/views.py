from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext as _

from utils.account import *
from account.forms import *
from utils.session import increase_session_value
from utils.email import send_verification_email

logger = logging.getLogger(__name__)

def login_request(request):
    if request.user.is_authenticated:
        messages.info(request, _('Already logged in!'))
        return redirect('home')

    if request.session.get('login_attempt', 0) > 9:
        messages.error(request, _('Try again later!'))
        return redirect('home')

    if request.method == "GET":
        form = LoginForm()
    
    else:
        form = LoginForm(request.POST)
        if form.is_valid():
            next_url = handle_user_login(form.cleaned_data, request)
            if next_url:        
                messages.success(request, _('Successfully Logged in!'))
                return redirect(next_url)
            
            increase_session_value(request, "login_attempt", 10)
            messages.warning(request, _("Email or password is wrong!"))

    return render(request, 'account/login.html', {
        'form' : form
    })


def register(request):
    if request.method == "GET":
        form = RegisterForm()
    
    else:
        form = RegisterForm(request.POST)
        if form.is_valid() and handle_user_register(form.cleaned_data, request):
            messages.success(request, _('Successfully Registered!'))
            return redirect('home')

    return render(request, 'account/register.html', {
        'form' : form
    })


def input_email(request):
    if request.method == "GET":
        form = InputEmailForm()

    else:
        form = InputEmailForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['email']
            try:
                send_verification_email(user_email, request)
            
            except Exception as email_error:
                logger.error(f"Email Verification Error -> {email_error}")
                messages.error(request, _('An error occured!'))
                return render(request, 'account/input_email.html', {
                    'form': form,
                    'error': _('Failed to send email. Please try again.')
                })
            
            request.session['current_email'] = user_email
            request.session['resend'] = 0
            request.session.set_expiry(5 * 60)
            return redirect('email_verification')

    return render(request, 'account/input_email.html', {
        'form' : form
    })


def email_verification(request):
    verification_code = request.session.get('verification_code', None)
    if verification_code == None:
        messages.error(request, _('Verification code expired!'))
        return redirect('input_email')
    
    if request.session.get('verification_attempt', 0) > 3:
        messages.error(request, _('Try again later!'))
        return redirect('home')
    
    if request.method == "GET":
        form = EmailVerificationForm()
    
    else:
        form = EmailVerificationForm(request.POST or None, request=request)
       
        if form.is_valid():
            request.session['email_verified'] = 'True'
            request.session['resend'] = 0
            return redirect('change_password_email')

    return render(request, 'account/email_verification.html', {
        'form' : form
    })


def resend_code(request):
    if request.session.get('resend', 0) > 3:
        messages.error(request, _("You've sent too many resend requests!"))
        return redirect('email_verification')

    user_email = request.session.get('current_email', '')
    try:
        send_verification_email(user_email, request)
        
    except Exception:
        messages.error(request, _('An error occured!'))
        return redirect('input_email')
    
    increase_session_value(request, "resend")
    return redirect('email_verification')


def change_password_email(request):
    if request.session.get('email_verified', None) == None:
        messages.error(request, _('Verification code expired!'))
        return redirect('input_email')

    if request.method == "GET":
        form = ChangePasswordEmailForm()

    else:
        form = ChangePasswordEmailForm(request.POST)
        
        if form.is_valid():
            user = get_object_or_404(User, email=request.session['current_email'])
            password1 = form.cleaned_data['password1']

            if user.check_password(password1):
                messages.info(request, _("The new password can't be same with the previous one!"))
                return redirect('login')                

            if 'email_verified' in request.session:
                del request.session['email_verified']
                
            request.session['resend'] = 0
            user.set_password(password1)
            user.save()

            messages.success(request, _('Your password was successfully updated!'))
            return redirect('login')

    return render(request, 'account/change_password_email.html', {
        'form' : form
    })


@login_required(login_url='/account/login')
def profile(request):
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profilemodel, files=request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, _('Successfully updated profile information!'))

    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profilemodel)

    return render(request, 'account/profile.html', {
        'profile_form' : profile_form,
        'user_form' : user_form
    })


@login_required(login_url='/account/login')
def change_password(request):
    if request.method == "GET":
        form = ChangePasswordForm()

    else:
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            user = request.user
            old_password = form.cleaned_data.get('old_password', '')

            if user.check_password(old_password):
                new_password = form.cleaned_data['password1']
                user.password = make_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, _('Successfully changed your password!'))

            else:
                messages.error(request, _('Input your current password right!'))

    return render(request, 'account/change_password.html', {
        'form' : form
    })


@login_required(login_url='/account/login')
def logout_request(request):
    request.session.flush()
    logout(request)
    messages.info(request, _('Logged out of your account!'))
    return redirect('home')