from random import randint

from django.core.mail import send_mail
from django.utils.translation import gettext as _


def send_contact_mail(cleaned_data: dict) -> None:
    name = cleaned_data.get('name', '')
    user_email = cleaned_data.get('email', '')
    subject = cleaned_data.get('subject', '')
    message = cleaned_data.get('message', '')

    send_mail(
        'Pdf Quiz Maker Contact Message',
        f'User name: {name}\n Email: {user_email}\nSubject: {subject}\nMessage: {message}',
        'settings.EMAIL_HOST_USER',
        ['youremail@email.com'],
        fail_silently=False,
    )


def send_verification_email(user_email: str, request) -> int:
    verification_code = str(randint(10000, 99_999))
    request.session['verification_code'] = verification_code

    send_mail(
        'Email Verification',
        _('Input this code to verify your email') + '\n' + str(verification_code),
        'settings.EMAIL_HOST_USER',
        [user_email],
        fail_silently=False,
    )

    return verification_code