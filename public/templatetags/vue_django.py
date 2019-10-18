from django.template import (
    Library, Node
)
from vue_django.utils import getContext
register = Library()


@register.tag('vue_django')
def vue(parser, token):

    return getContext()
