from django.conf import settings
from django.contrib.auth import logout
from django.utils import timezone


class AutoLogout:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            return self.get_response(request)

        now = timezone.now().timestamp()
        last_activity = request.session.get('last_activity')
        if last_activity and now - float(last_activity) > settings.AUTO_LOGOUT_TIME:
            logout(request)
        else:
            request.session['last_activity'] = now

        return self.get_response(request)
