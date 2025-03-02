from datetime import datetime, timedelta
import json

from django.core.serializers.json import DjangoJSONEncoder


def set_session_with_expiration(request, key, value, expiration_minutes):
    expiration_time = datetime.now() + timedelta(minutes = expiration_minutes)
    
    data_to_store = {
        'value': value,
        'expiration_time': expiration_time
    }
    
    request.session[key] = json.dumps(data_to_store, cls=DjangoJSONEncoder)