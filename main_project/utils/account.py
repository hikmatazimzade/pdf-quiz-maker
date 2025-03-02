from typing import Optional

from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate


def handle_user_login(cleaned_data: dict, request) -> Optional[str]:
    email = cleaned_data['email']
    password = cleaned_data['password']

    user_object = User.objects.filter(email=email).first()
    if user_object is None:
        return None
    
    user = authenticate(request, username=user_object.username,
                        password=password)
    if user is not None:
        if cleaned_data.get("remember_me", False):
            request.session.set_expiry(365 * 86_400)
        else:
            request.session.set_expiry(7 * 86_400)

        login(request, user)
        request.session['login_attempt'] = 0

        next_url = request.GET.get('next', 'home')
        return next_url