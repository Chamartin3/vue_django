from django.conf import settings
from importlib import import_module
import json
from django.middleware.csrf import get_token
from django.utils.html import mark_safe

api= import_module(getattr(settings, "DJV_API_URLS", None ))


class APIMap(object):
    """docstring for APIMap."""

    def __init__(self, api):
        self.api = api
        self.modules = self.processAPIPaths(api)
    

    def processAPIPaths(self, api):
        '''  Genetates a map of paths and actions that can be taken every case '''

        # Iterates over each route as a Model it does note take into acounts un routed paths
        # proaccess='api.urlpatterns'
        modules={}
        for idx, path in [(i,p) for (i, p) in enumerate(self.api.urlpatterns) if p.callback is None]:
            modules[self.getName(path)] = self.processRoutes(path)
        # print(json.dumps(modules, indent=2))
        return modules




def get_routes(api):
    ''' gets all the paths that interacts with the aplication '''

    # Paths that have an asociated route (this are also the paths where a aplication is redirectes if the vue routed does not match a page )
    # TODO: filter these by autehcticationm
    navigation_paths= getattr(settings, "DJV_NAVIGATION", [''])

    # Paths that are excluded from the api
    excluded_routes= getattr(settings, "DJV_EXCLUDED_ROUTES", [''])

    # base route API (is the url where the api es located)I
    api_baseroute= getattr(settings, "DJV_API_ROUTE", 'api/')

    redir_paths=[{ 'redirect':f'/{p}', 'path': f'/{p}*'} for p in navigation_paths]

    # model routes is where the complete models are locatedb (Model Viewset)
    # TODO: Read also the routes from none Viewset routes
    model_routes = [url.pattern._regex for url in api.urlpatterns if url.pattern._regex not in excluded_routes],

    return {
    'api_route':api_baseroute,
    'model_routes':model_routes[0],
    'navigation_paths':redir_paths,
    }

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
        'token':get_token(request),
        **get_routes(api)
        }

    return {'vue_django_vars':mark_safe(json.dumps(context))}
