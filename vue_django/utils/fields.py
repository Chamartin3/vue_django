from rest_framework.relations import ( RelatedField,
    HyperlinkedIdentityField, HyperlinkedRelatedField, ManyRelatedField,
    PrimaryKeyRelatedField, RelatedField, SlugRelatedField, StringRelatedField,
)
from rest_framework.serializers import ModelSerializer

def get_model_fields(serializer_class):
    '''
    TODO: read the fields and generate a list of validators that can be replicated 
    in the vue aplication
    '''
    instance = serializer_class()
    fields = {}
    relation_classes = [
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

            field = {}
            field['related'] = False
            field['_kwargs'] = [ str(x) for x in getattr( f, '_kwargs', []) ]
            field['label'] = str(getattr( f, 'label', None))
            field['help_text'] = str(getattr( f, 'help_text', None))
            field['allow_null']= getattr( f, 'allow_null', False)
            field['allow_blank']= getattr( f, 'allow_blank', False)
            field['read_only']= getattr( f, 'read_only', False)
            validators=[v.__class__.__name__ for v in getattr(f, '_validators', [])]
            field['_validators'] = validators
            fields[f.field_name] = field

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
                    field['related_model'] = qs.model.__name__
                else:
                    field['related_model'] = rf.field_name
                field['_kwargs'] = [str(x) for x in getattr(rf, '_kwargs', [])]
                field['label'] = str(getattr(rf, 'label', None))
                field['help_text'] = str(getattr(rf, 'help_text', None))
                field['required'] = getattr(rf, 'required', False)
                validators = [v.__class__.__name__ for v in getattr(rf, '_validators', [])]
                field['_validators'] = validators
                fields[rf.field_name] = field

            elif issubclass(rf.__class__, ModelSerializer):
                field['related'] = True
                field['related_model'] = rf.Meta.model.__name__
                field['_kwargs'] = [str(x) for x in getattr(f, '_kwargs', [])]
                field['label'] = str(getattr(f, 'label', None))
                field['help_text'] = str(getattr(f, 'help_text', None))
                field['allow_null'] = getattr(f, 'allow_null', False)
                field['allow_blank'] = getattr(f, 'allow_blank', False)
                field['read_only'] = getattr(f, 'read_only', False)
                validators = [v.__class__.__name__ for v in getattr(f, '_validators', [])]
                field['_validators'] = validators
                fields[f.field_name] = field
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