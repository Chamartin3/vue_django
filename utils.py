from django.conf import settings

from django.middleware.csrf import get_token


def get_authentication():
    on_login= getattr(settings, "LOGIN_URL", None )
    on_logout= getattr(settings, "LOGOUT_REDIRECT_URL", None )
    redir= getattr(settings, "LOGIN_REDIRECT_URL", None)
    auth_path= getattr(settings, "DLV_AUTH_PATH", None)
    #
    return {
        'on_logout':on_logout,
        'on_login':redir,
        'auth_path':auth_path
    }


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


    context =  {
        'auth':get_authentication,
        'user':user, 
        'token':get_token(request) }

    return {'vue_django_vars':mark_safe(json.dumps(context))}
