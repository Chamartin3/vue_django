from django.conf import settings
from django.utils.encoding import smart_str
from django.middleware.csrf import get_token
from .serializers import GroupsSerializer, PermissionSerializer
from .api_map import ApiMap
from importlib import import_module


# Autentication GlobalVariables
LOGIN_URL = getattr(settings, "LOGIN_URL", None )
LOGOUT_REDIRECT_URL = getattr(settings, "LOGOUT_REDIRECT_URL", None )
LOGIN_REDIRECT_URL = getattr(settings, "LOGIN_REDIRECT_URL", None)

# Vue Django GlobalVariables
DLV_AUTH_PATH = getattr(settings, "DLV_AUTH_PATH", None)
DJV_NAVIGATION = getattr(settings, "DJV_NAVIGATION", [''])
DJV_EXCLUDED_ROUTES = getattr(settings, "DJV_EXCLUDED_ROUTES", [''])
DJV_API_ROUTE = getattr(settings, "DJV_API_ROUTE", 'api/')
DJV_API_URLS = getattr(settings, "DJV_API_URLS", None )

def get_authentication():
    on_login = LOGIN_URL
    on_logout = LOGOUT_REDIRECT_URL
    redir = LOGIN_REDIRECT_URL
    auth_path = DLV_AUTH_PATH
    #
    return {
        'on_logout':on_logout,
        'on_login':redir,
        'auth_path':auth_path
    }

def get_auth_user(request):
    ''' returns all the Autentication information for the current user'''
    if request.user.is_authenticated:
        user = {
        'id':request.user.pk,
        'username':request.user.username,
        'first_name':request.user.first_name,
        'last_name':request.user.last_name,
        'email':request.user.email,
        'permissions':[{'id':p.pk} for p in request.user.user_permissions.all()],
        'groups':[{'id':g.pk, 'name':g.name} for g in request.user.groups.all()]
        }
    else:
        user = request.user.is_authenticated
    return user


def get_routes(api):
    ''' gets all the paths that interacts with the aplication '''

    # Paths that have an asociated route (this are also the 
    # paths where a aplication is redirectes if the vue routed does not match a page )
    # TODO: filter these by autehcticationm
    navigation_paths = DJV_NAVIGATION

    # Paths that are excluded from the api
    excluded_routes = DJV_EXCLUDED_ROUTES

    # base route API (is the url where the api es located)I
    api_baseroute = DJV_API_ROUTE

    redir_paths=[{ 'redirect':f'/{p}', 'path': f'/{p}*'} for p in navigation_paths]

    # model routes is where the complete models are locatedb (Model Viewset)
    # TODO: Read also the routes from none Viewset routes
    model_routes = [url.pattern._regex for url in api.urlpatterns if url.pattern._regex not in excluded_routes],

    return {
        'api_route':api_baseroute,
        'model_routes':model_routes[0],
        'navigation_paths':redir_paths,
    }


def generate_django_context(request):
    api = import_module(DJV_API_URLS)
    map = ApiMap(api)
    context = {
        'user': get_auth_user(request),
        'csrf_token': get_token(request),
        'autentication': get_authentication(),
        '_actions': map.modelMap,
        **get_routes(api)
        }
    return context