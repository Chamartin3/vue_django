from django.conf import settings



def get_context_object(request):
    
    if request.user.is_authenticated:
        user = request.user
    else
        user = request.user.is_authenticated

    return user
