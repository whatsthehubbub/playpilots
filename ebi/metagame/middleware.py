from django.contrib.auth.views import logout_then_login, login
from django.http import HttpResponseRedirect

class SiteLogin:
    def process_request(self, request):
        if request.user.is_anonymous() and 'login' not in request.path:
            if not request.POST:
                return HttpResponseRedirect('/login/?next=%s' % request.path)