import json
from .utils import generate_django_context
from django.utils.html import mark_safe
from django.views.generic import TemplateView



class VueDjangoConfig(TemplateView):
    template_name="vue_django.js"

    def get_context_data(self, **kwargs):
        context = json.dumps( generate_django_context(self.request) )
        return {'vue_django_vars':mark_safe(context)}
