from typing import Optional
import logging

from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate

logger = logging.getLogger(__name__)

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


def handle_user_register(cleaned_data: dict, request) -> bool:
    try:
        first_name = cleaned_data['first_name']
        last_name = cleaned_data['last_name']
        username = cleaned_data['username']
        email = cleaned_data['email']
        password = cleaned_data['password1']

        User.objects.create_user(first_name=first_name, last_name=last_name,
                            username=username, email=email, password=password)
        
        user = authenticate(request, username = username, password = password)
        login(request, user)
        return True

    except Exception as register_error:
        logger.error(f"Register Error -> {register_error}")
        return False