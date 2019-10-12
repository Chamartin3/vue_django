from django.conf import settings
from importlib import import_module
import json
from django.middleware.csrf import get_token
from django.utils.html import mark_safe
from rest_framework.relations import ( RelatedField,
    HyperlinkedIdentityField, HyperlinkedRelatedField, ManyRelatedField,
    PrimaryKeyRelatedField, RelatedField, SlugRelatedField, StringRelatedField,
)


api= import_module(getattr(settings, "DJV_API_URLS", None ))


class APIMap(object):
    """docstring for APIMap."""

    def __init__(self, api):
        self.api = api
        self.modules = self.processAPIPaths(api)
        self.modelMap = self.generateModels()


    def simplifiedEndpoint(self, pattern):
        # We dont need a diferent route to specify thr format so we remove them and unify them
        return pattern.replace('\.(?P<format>[a-z0-9]+)/?$','/$')


    def get_model_fields(self, serializer_class):
        instance =serializer_class()
        fields={}
        relation_classes= [
            HyperlinkedIdentityField,
            HyperlinkedRelatedField,
            ManyRelatedField,
            PrimaryKeyRelatedField,
            RelatedField,
            SlugRelatedField,
            StringRelatedField,
        ]

        try:
            for f in instance._writable_fields:
                field={}
                field['related']=False
                field['_kwargs']=[str(x) for x in getattr(f, '_kwargs', [])]
                field['label']=str(getattr(f, 'label', None))
                field['help_text']=str(getattr(f, 'help_text', None))
                field['allow_null']=getattr(f, 'allow_null', False)
                field['allow_blank']=getattr(f, 'allow_blank', False)
                field['read_only']=getattr(f, 'read_only', False)
                validators=[v.__class__.__name__ for v in getattr(f, '_validators', [])]
                field['_validators']=validators
                fields[f.field_name]=field

            for rf in instance._readable_fields:
                if rf.__class__ in relation_classes:
                    # import pdb; pdb.set_trace()
                    field['related']=True

                    child_relation=getattr(rf, 'child_relation', None)
                    if child_relation is not None:
                        qs=getattr(child_relation, 'queryset', None)
                    else:
                        qs=None

                    if qs is not None:
                        field['related_model']=qs.model.__name__
                    else:
                        field['related_model']=rf.field_name

                    field['_kwargs']=[str(x) for x in getattr(rf, '_kwargs', [])]
                    field['label']=str(getattr(rf, 'label', None))
                    field['help_text']=str(getattr(rf, 'help_text', None))
                    field['required']=getattr(rf, 'required', False)
                    validators=[v.__class__.__name__ for v in getattr(rf, '_validators', [])]
                    field['_validators']=validators
                    fields[rf.field_name]=field

                elif issubclass(rf.__class__, ModelSerializer):
                    field['related']=True
                    field['related_model']=rf.Meta.model.__name__
                    field['_kwargs']=[str(x) for x in getattr(f, '_kwargs', [])]
                    field['label']=str(getattr(f, 'label', None))
                    field['help_text']=str(getattr(f, 'help_text', None))
                    field['allow_null']=getattr(f, 'allow_null', False)
                    field['allow_blank']=getattr(f, 'allow_blank', False)
                    field['read_only']=getattr(f, 'read_only', False)
                    validators=[v.__class__.__name__ for v in getattr(f, '_validators', [])]
                    field['_validators']=validators
                    fields[f.field_name]=field

                else:
                    if rf not in instance._writable_fields and rf.field_name is not 'id':
                        # print(rf.field_name)
                        pass
        except Exception as e:
            # raise e
            # print(e)
            # print(serializer_class)
            pass
        return fields

    def processCallback(self, path):

        if path.name == 'api-root':
            return None
        endpoint={}
        endpoint['name']=path.name

        if issubclass(path.callback.cls, ModelViewSet):
            view = path.callback.cls
            # print('\t \t  Is Model Viewset')
            # print('\t \t '+path.pattern._regex)

            endpoint['endpoint'] = self.simplifiedEndpoint(path.pattern._regex)
            methods = [k.upper() for k in path.callback.actions.keys()]
            endpoint['methods'] = methods
            endpoint['fields'] = self.get_model_fields(view.serializer_class)
            # metodos_permitidos=[m.upper() for m in view.http_method_names if hasattr(view, m)]
            # print('\t  \t'+str(metodos_permitidos))
            # print(access+'.callback.cls')

        elif issubclass(path.callback.cls, APIView):
            # print('\t  \t  Is APIView')
            # print('\t  \t'+path.pattern._route)
            endpoint['endpoint'] = path.pattern._route
            view=path.callback.cls
            methods=[m.upper() for m in view.http_method_names if hasattr(view, m) and m.upper() != 'OPTIONS']
            endpoint['methods'] = methods
            if hasattr(view, 'serializer_class'):
                endpoint['fields'] = self.get_model_fields(view.serializer_class)
            else:
                endpoint['fields'] = None
            # print('\t  \t'+str(metodos_permitidos))
            # print(access+'.callback.cls')
        return endpoint

    def getName(self, path):
        if getattr(path, 'namespace'):
            return path.namespace
        return path.pattern._regex.strip('/')

    def processSubRoutes(self, sub_route):
        end_points=[]
        actions={}
        for (ind, pattern) in enumerate(sub_route):
            if pattern.callback is not None:
                # print('\t'+pattern.name)
                endpoint= self.processCallback(pattern) if pattern.name is not None else None
                if endpoint is not None:
                    actions[endpoint['name']]={
                        'route':endpoint['endpoint'],
                        'methods':endpoint['methods'],
                        'fields':endpoint['fields']
                    }
        # import pdb; pdb.set_trace()
        return actions

    def processRoutes(self, path):
        # print(idx)
        # print(path.pattern._regex)
        sub_route=path.urlconf_name.urlpatterns
        actions=self.processSubRoutes(sub_route)

        module={}
        module['module_path'] = path.pattern._regex
        module['actions'] = actions
        # import json
        # print(json.dumps(module, indent=2))
        # access=proaccess+f'[{idx}]'+'.urlconf_name.urlpatterns'
        return module

    def processAPIPaths(self, api):
        '''  Genetates a map of paths and actions that can be taken every case '''

        # Iterates over each route as a Model it does note take into acounts un routed paths
        # proaccess='api.urlpatterns'
        modules={}
        for idx, path in [(i,p) for (i, p) in enumerate(self.api.urlpatterns) if p.callback is None]:
            modules[self.getName(path)] = self.processRoutes(path)
        # print(json.dumps(modules, indent=2))
        return modules


    def processFullpath(self, fullpath):
        pathsWRegex= re.sub(r'[^a-zA-Z/<>:]', '', fullpath.replace('P<','<')).replace('//','/')
        params=re.findall(r'<(.*?)>',pathsWRegex)

        descParams=[]
        for param in params:
            descParam={}
            paramArray=param.split(':')
            if len(paramArray)>1:
                descParam['name']=paramArray[1]
                descParam['type']=paramArray[0]
            else:
                descParam['name']=paramArray[0]
                descParam['type']='any'
            descParams.append(descParam)

        pieces=re.split('<|>',pathsWRegex)
        res={
            'path':pathsWRegex,
            'params':descParams,
            'pieces':pieces
        }

        return res

    def generateActionList(self):

        actions=[]
        for m_name, module in self.modules.items():
            for a_name, action in module['actions'].items():
                methods_per_action=len(action['methods'])
                for m in action['methods']:
                    act={}
                    act['unique'] = methods_per_action < 2
                    act['type'] = m
                    act['basepath'] = module['module_path']
                    act['route'] = self.processFullpath(module['module_path']+action['route'])
                    act['fields'] = action['fields']
                    act['endpoint_name'] = a_name
                    act['module_name'] = m_name
                    actions.append(act)
        return actions

    def getNamespace(self, a):
        ep=a['endpoint_name'].split('-')
        if len(ep)>1:
            return True, ep[0]
        return  False ,a['module_name']

    def generateModels(self):
        actions=self.generateActionList()
        models={}
        for a in actions:
            is_namespace, model_name=self.getNamespace(a)
            if is_namespace:
                a['name']=a['endpoint_name'].replace(f'{model_name}-','')
            else:
                a['name']=a['endpoint_name']

            model_in_list=models.get(model_name,None)
            if model_in_list is None:
                models[model_name]=[]

            models[model_name].append(a)
        return models


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
