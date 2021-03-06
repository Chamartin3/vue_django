from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from .fields import get_model_fields
import re


class APIReader(object):
    """
        API Reader Reads the routes and gerates a model
    """
    def __init__(self, api):
        self.modules = self.processAPIPaths(api)

    def simplifiedEndpoint(self, pattern):
        '''
        removes the rgeex from the enpoint
        '''
        # We dont need a diferent route to specify thr format so we remove them and unify them
        return pattern.replace('\.(?P<format>[a-z0-9]+)/?$','/$')
  
    def processCallback(self, path):
        '''
        Reads the callback of the path and returns a action and the fields
        '''

        if path.name == 'api-root':
            return None
        endpoint={}
        endpoint['name']=path.name

        if issubclass(path.callback.cls, ModelViewSet):
            view = path.callback.cls
            endpoint['endpoint'] = self.simplifiedEndpoint(path.pattern._regex)
            methods = [ k.upper() for k in path.callback.actions.keys() ]
            endpoint['methods'] = methods
            endpoint['fields'] = get_model_fields(view.serializer_class)


        elif issubclass(path.callback.cls, APIView):
            endpoint['endpoint'] = path.pattern._route
            view=path.callback.cls
            methods=[m.upper() for m in view.http_method_names if hasattr(view, m) and m.upper() != 'OPTIONS']
            endpoint['methods'] = methods
            if hasattr(view, 'serializer_class'):
                endpoint['fields'] = get_model_fields(view.serializer_class)
            else:
                endpoint['fields'] = None
        return endpoint

    def processSubRoutes(self, sub_route):
        '''
        Estructrure each endpoint as a dicrionary reading the callback
        '''
        # end_points= []
        actions = {}
        for (ind, pattern) in enumerate(sub_route):
            if pattern.callback is not None:
                endpoint= self.processCallback(pattern) if pattern.name is not None else None
                if endpoint is not None:
                    actions[endpoint['name']]={
                        'route': endpoint['endpoint'],
                        'methods': endpoint['methods'],
                        'fields': endpoint['fields']
                    }
        return actions

    def processRoutes(self, path):
        '''
        Reads each path as a module
        '''
        sub_route = path.urlconf_name.urlpatterns
        actions = self.processSubRoutes(sub_route)
        module = {}
        module['module_path'] = path.pattern._regex
        module['actions'] = actions
        return module
    
    def getName(self, path):
        '''
            Gets the endpoint name
        '''
        if getattr(path, 'namespace'):
            return path.namespace
        return path.pattern._regex.strip('/')

    def processAPIPaths(self, api):
        '''  Genetates a map of paths and actions that can be taken every case 
        Iterates over each route as a Model it does note take into acounts un routed paths
        '''
        modules={}
        for idx, path in [ (i,p) for (i, p) in enumerate(api.urlpatterns) if p.callback is None ]:
            modules[self.getName(path)] = self.processRoutes(path)
        return modules




class APIMap(object):
    """APIMap  utility class that process ana endpoint and 
    returns a list with all the actions methods an lists contian each one """

    def __init__(self, api):
        reader = APIReader(api)
        self.modules = reader.modules
        self.api = api
        self.modelMap =  self.generateModels()
    

    def processFullpath(self, fullpath):
        '''
        Reads the  information inside a path and process it to fenerate a path dictionary 
        '''
        pathsWRegex = re.sub(r'[^a-zA-Z/<>:]', '', fullpath.replace('P<','<')).replace('//','/')
        params = re.findall(r'<(.*?)>',pathsWRegex)

        descParams = []
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

        pieces = re.split('<|>',pathsWRegex)
        res = {
            'path':pathsWRegex,
            'params':descParams,
            'pieces':pieces
        }

        return res

    def generateActionList(self):
        '''
        Generates a list of actions readng the HTML Endpoints in 
        in the modules list
        '''

        actions=[]
        for m_name, module in self.modules.items():
            for a_name, action in module['actions'].items():
                methods_per_action=len(action['methods'])
                for m in action['methods']:
                    act={}
                    act['unique'] = methods_per_action < 2
                    act['type'] = m
                    act['basepath'] = module['module_path']
                    act['route'] = self.processFullpath(module['module_path'] + action['route'])
                    act['fields'] = action['fields']
                    act['endpoint_name'] = a_name
                    act['module_name'] = m_name
                    actions.append(act)
        return actions

    def getNamespace(self, a):
        '''
        Gets the namespace used to define the endpoint name, from an enpoint dicctionary 
        '''
        ep = a['endpoint_name'].split('-')
        if len(ep) > 1:
            return True, ep[0]
        return  False , a['module_name']

    def generateModels(self):
        ''' Generates the final iteration of the models
            from the action list 
        '''
        actions = self.generateActionList()
        models = {}
        for a in actions:
            is_namespace, model_name = self.getNamespace(a)
            if is_namespace:
                a['name']=a['endpoint_name'].replace(f'{model_name}-','')
            else:
                a['name']=a['endpoint_name']

            model_in_list=models.get(model_name,None)
            if model_in_list is None:
                models[model_name]=[]

            models[model_name].append(a)
        return models
