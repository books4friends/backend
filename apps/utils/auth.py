from django.http.response import HttpResponse


def is_user_authenticated(request):
    return not not (request.session.get('vk_id') and request.session.get('access_token'))


def auth_decorator(function):
    def wrap(self, request, *args, **kwargs):
        if is_user_authenticated(request):
            return function(self, request, *args, **kwargs)
        else:
            return HttpResponse('Unauthorized', status=401)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

