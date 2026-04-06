from accounts.models import CustomAnonymousUser


class CustomAnonymousUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            request.user = CustomAnonymousUser()
        return self.get_response(request)