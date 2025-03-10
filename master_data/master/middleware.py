import time
from .models import *
from django.conf import settings
from django.contrib.auth import logout, get_user_model
from django.utils import timezone
from django.utils.timezone import now
from django.contrib.auth.models import *

class AutoLogout :
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated :
            return self.get_response(request)
        
        max_idle_time = getattr(settings, 'AUTO_LOGOUT_TIME', int(60 * 60 * 2))

        last_activity = request.session.get('last_activity')
        if last_activity :
            if '+' in last_activity or '-' in last_activity :
                last_activity_time = timezone.datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S.%f%z')
            else :
                last_activity_time = timezone.datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S.%f')
            idle_time = (timezone.now() - last_activity_time).seconds
            if idle_time > max_idle_time :
                logout(request)

        request.session['last_activity'] = str(timezone.now())

        return self.get_response(request)