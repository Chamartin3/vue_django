from django.conf import settings
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.serializers import ModelSerializer

from .serializers import GroupsSerializer, PermissionSerializer
from rest_framework.relations import ( RelatedField,
    HyperlinkedIdentityField, HyperlinkedRelatedField, ManyRelatedField,
    PrimaryKeyRelatedField, RelatedField, SlugRelatedField, StringRelatedField,
)

from .api_map import ApiMap

import json
import re
from django.utils.encoding import smart_str

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

def get_auth_user(request):
    ''' returns all the Autentication information for the current user'''
    if request.user.is_authenticated:
        user= {
        'id':request.user.pk,
        'username':request.user.username,
        'first_name':request.user.first_name,
        'last_name':request.user.last_name,
        'email':request.user.email,
        'permissions':PermissionSerializer(request.user.user_permissions.all(), many=True).data,
        'groups':GroupsSerializer(request.user.groups.all(), many=True).data,
        # 'picture':request.user.profile.pic_url
        }
    else:
        user=request.user.is_authenticated
    # returns all the Autentication information
    return user


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