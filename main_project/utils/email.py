from django.core.mail import send_mail


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