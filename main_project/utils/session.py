from datetime import datetime, timedelta
import json

from django.core.serializers.json import DjangoJSONEncoder


def set_session_with_expiration_json(request, key, value, expiration_minutes):
    expiration_time = datetime.now() + timedelta(minutes=expiration_minutes)
    
    data_to_store = {
        'value': value,
        'expiration_time': expiration_time
    }
    
    request.session[key] = json.dumps(data_to_store, cls=DjangoJSONEncoder)


def increase_session_value(request, value, expiration_minutes: int=None) -> None:
    session_value = request.session.get(value, 0)
    session_value += 1
    
    request.session[value] = session_value
    if expiration_minutes:
        request.session.set_expiry(expiration_minutes * 60)