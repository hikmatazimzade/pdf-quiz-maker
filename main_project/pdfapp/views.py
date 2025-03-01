import json
import base64
from datetime import datetime, timedelta
import logging

from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.http import JsonResponse

from pdfapp.tasks import create_quiz_task
from pdfapp.forms import Contact_Form, Quiz_Form, Edit_Quiz_Form
from pdfapp.models import Quiz_Model
from account.models import Profile_Model
from utils.quiz import *

logger = logging.getLogger(__name__)

def home(request):
    return render(request, "pdfapp/home.html")


@login_required(login_url = '/account/login')
def quiz(request, slug):
    quiz_settings = fetch_quiz_settings(request, slug)
    if quiz_settings is None:
        messages.error(request, _("This quiz doesn't exist!"))
        return redirect('quiz_choice')        
    
    try:
        quiz_data = get_quiz_data(quiz_settings["tests"],
            quiz_settings["first_boundary"], quiz_settings["last_boundary"])

    except Exception as quiz_data_error:
        logger.error(f"Error Occurred In Quiz Opening -> {quiz_data_error}")
        messages.error(request, _('An error occured!'))
        return redirect('home')
    
    test_number = quiz_settings["test_number"]
    if test_number > len(quiz_data) or test_number < 1:
        messages.error(request, 
            _('There are not this many questions in this quiz!'))
        return redirect('quiz_choice')
    
    if quiz_settings["shuffle_variant"]:
        shuffle_quiz_data(quiz_data, test_number)
    
    return render(request, 'pdfapp/quiz.html', {
        'quiz_data' : quiz_data,
        'show_number' : quiz_settings["show_number"]
    })


@login_required(login_url = '/account/login')
def edit_quiz(request, slug):
    quiz_settings = fetch_edit_quiz_settings(request, slug)
    if quiz_settings is None:
        messages.error(request, _("This quiz doesn't exist!"))
        return redirect('quiz_choice')

    if request.method == "GET":
        form = initialize_edit_form(quiz_settings)

    else:
        form = process_edit_form(request, quiz_settings)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            try:
                first_boundary = int(request.POST.get('slider1', 1))
                last_boundary = int(request.POST.get('slider2', 2))
                user_quiz = Quiz_Model.objects.get(user = request.user, slug = slug)

                edit_user_quiz(user_quiz, cleaned_data["quiz_name"],
                cleaned_data["test_number"], cleaned_data["show_number"],
                cleaned_data["shuffle_variant"],
                first_boundary, last_boundary)
                
                edit_user_cache_form(request, slug, quiz_settings, cleaned_data, 
                                first_boundary, last_boundary)
            
            except Exception as quiz_edit_error:
                logger.error(f"Error While Editing Quiz -> {quiz_edit_error}")
                messages.error(request, _('An error occured!'))
                return redirect("quiz_choice")
    
            messages.success(request, _('Successfully saved!'))
            return redirect('quiz_choice')

    return render_quiz_edit_page(request, form, quiz_settings, slug)


@login_required(login_url = '/account/login')
def delete_quiz(request, slug):
    try:
        Quiz_Model.objects.get(slug = slug, user = request.user).delete()

        profile_model = Profile_Model.objects.get(user = request.user)
        profile_model.current_quiz_number -= 1
        profile_model.save()

        messages.success(request, _('Quiz successfully deleted!'))
    except Exception as delete_quiz_error:
        logger.error(f"Quiz Deleting Error -> {delete_quiz_error}")
        messages.error(request, _("This quiz doesn't exist!"))

    return redirect('quiz_choice')


def set_session_with_expiration(request, key, value, expiration_minutes):
    expiration_time = datetime.now() + timedelta(minutes = expiration_minutes)
    
    data_to_store = {
        'value': value,
        'expiration_time': expiration_time
    }
    
    request.session[key] = json.dumps(data_to_store, cls=DjangoJSONEncoder)


def convert_file_to_base64(file_content):
    return base64.b64encode(file_content).decode('utf-8')


@login_required(login_url = '/account/login')
def check_quiz_status(request):
    user_id = request.user.id
    status_data = cache.get(f"cre_stat_{user_id}")
    if status_data:
        return JsonResponse(status_data)
    else:
        return JsonResponse({"status": "pending"})


@login_required(login_url = '/account/login')
def create_quiz(request):
    if request.method == "GET":
        form = Quiz_Form()

    else:
        quiz_attempt = request.session.get('quiz_attempt', None)
        if quiz_attempt:
            quiz_attempt = json.loads(quiz_attempt)
            
            if quiz_attempt.get('value', 0) > 5:
                current_time = datetime.now()
                expiration_time = datetime.fromisoformat(quiz_attempt.get('expiration_time', str(current_time)))

                if current_time > expiration_time:
                    del request.session['quiz_attempt']
                    
                '''else:
                    remaining = (expiration_time - current_time).seconds
                    remaining //= 60
                    remaining += 1
                    minute_text = 'minutes'
                    if remaining == 1 : minute_text = 'minute'
                    messages.error(request, _('You have uploaded many PDFs recently; please try again {remaining} {minute_text} later!').format(remaining = remaining, minute_text = minute_text))
                    return redirect('home')'''
            
        try:
            profile_model = Profile_Model.objects.get(user = request.user)
            if profile_model.current_quiz_number >= 8:
                messages.error(request, _('The maximum quiz limit for each account is 8!'))
                return redirect('home')

        except Exception as profile_error:
            logger.error(f"Profile Model Error -> {profile_error}")
            return redirect('home')


        form = Quiz_Form(request.POST or None, request.FILES, request = request)
        if form.is_valid():
            try:
                slider1 = int(request.POST.get('slider1', 1))
                slider2 = int(request.POST.get('slider2', 2))
                
                
            except:
                return redirect('quiz_choice')
            
            
            attempt = request.session.get('quiz_attempt', 0)
            
            if attempt:
                quiz_attempt = json.loads(attempt).get('value', 0)

            else:
                quiz_attempt = 0


            quiz_attempt += 1
            set_session_with_expiration(request, key = 'quiz_attempt', value = quiz_attempt, expiration_minutes = 5)
            
            try:
                uploaded_file = request.FILES['pdf']
                file_content = uploaded_file.read()
                base64_content = convert_file_to_base64(file_content)


                variant_number = form.cleaned_data.get('variant_number', 0)
                quiz_name = form.cleaned_data.get('quiz_name', '')
                test_number = form.cleaned_data.get('test_number', 0)
                show_number = form.cleaned_data.get('show_number', False)
                shuffle_variant = form.cleaned_data.get('shuffle_variant', False)


                create_quiz_task.delay(request.user.id, base64_content, variant_number, quiz_name, test_number, show_number, shuffle_variant, slider1, slider2)
                return render(request, "pdfapp/load_page.html")
            

                
            except Exception:
                messages.error(request, _('An error occured!'))
                return redirect('create_quiz')
            


    return render(request, 'pdfapp/create_quiz.html', {
        'form' : form
    })


@login_required(login_url = '/account/login')
def quiz_choice(request):
    quizzes = Quiz_Model.objects.filter(user = request.user)
    return render(request, 'pdfapp/quiz_choice.html', {
        'quizzes' : quizzes
    })


@login_required(login_url = "/account/login")
def success_quiz_choice(request):
    messages.success(request, _("Quiz successfully created!"))
    return redirect("quiz_choice")


@login_required(login_url = "/account/login")
def create_error(request):
    error_dict = cache.get(f"cre_stat_{request.user.id}", {})
    error_message = error_dict.get("message", "An error occured!")

    messages.error(request, _(error_message))
    return redirect("create_quiz")


def about(request):
    return render(request, 'pdfapp/about.html')


def contact(request):
    if request.method == "GET":
        form = Contact_Form()

    else:
        if request.session.get('contact_attempt', 0) > 3:
            messages.error(request, _('You have sent too many messages!'))
            return redirect('contact')
        
        form = Contact_Form(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name', '')
            user_email = form.cleaned_data.get('email', '')
            subject = form.cleaned_data.get('subject', '')
            message = form.cleaned_data.get('message', '')
            
            try:
                send_mail(
                    'Pdf Quiz Maker Contact Message',
                    f'User name: {name}\n Email: {user_email}\nSubject: {subject}\nMessage: {message}',
                    'settings.EMAIL_HOST_USER',
                    ['youremail@email.com'],
                    fail_silently=False,
                )
                messages.success(request, _("Your message was successfully sent!"))
            
            except Exception as email_error:
                logger.error(f"An Error Occured While Sending Email -> {email_error}")
                messages.error(request, _('An error occured!'))
                return redirect('contact')
            
            contact_attempt = request.session.get('contact_attempt', 0)
            request.session['contact_attempt'] = contact_attempt + 1

            
            return redirect('contact')

    return render(request, 'pdfapp/contact.html', {
        'form' : form
    })


def load_page(request):
    return render(request, "pdfapp/load_page.html")


@cache_page(None)
def user_guide(request):
    return render(request, 'pdfapp/user_guide.html')


def buy_me_coffee(request):
    return render(request, 'pdfapp/buy_me_coffee.html')


def not_found(request, exception):
    return render(request, 'partials/not_found.html', status = 404)