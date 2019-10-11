from django.conf import settings

from django.middleware.csrf import get_token

def get_context_object(request):
    
    if request.user.is_authenticated:
        user = request.user
    else
        user = request.user.is_authenticated

    return {
        'user':user, 'token':get_token(request)
