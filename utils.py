from django.conf import settings

from django.middleware.csrf import get_token

def get_context_object(request):
    
    if request.user.is_authenticated:
        user= {
        'id':request.user.pk,
        'username':request.user.username,
        'first_name':request.user.first_name,
        'last_name':request.user.last_name,
        'email':request.user.email,
        'permissions':request.user.user_permissions.all(),
        'groups':request.user.groups.all(),
        }
    else
        user = request.user.is_authenticated

    context =  {'user':user, 'token':get_token(request) }

    return {'vue_django_vars':mark_safe(json.dumps(context))}
