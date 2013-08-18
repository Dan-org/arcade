import os, re, urlparse
import ttag
from xml.etree import ElementTree

from django import template
from django.core.urlresolvers import reverse
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.template.defaulttags import URLNode, url
from django.template import Template
from django.template import Context
from django.template import loader
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response

from django.utils.encoding import force_unicode

from django.conf import settings

register = template.Library()


@register.tag(name="gamepieces")
class PiecesTag(ttag.Tag):
    """
    Tag will ...
    
    Usage:
        {% pieces 'my_game_name' %}
    
    """
    game = ttag.Arg()    

    def render(self, context):        
        data = self.resolve(context)   
        game = data['game']
        #game_dir = "/%s%s/" % (settings.ARCADE_URL, game)
        url = "%s/%s/assets.html" % (settings.ARCADE_PATH, game)
        text = open(url, 'rb').read()
        t = Template(text)
        c = Context({ 'STATIC_URL' : '/static/' })        
        return t.render(c)


@register.tag(name="gameboard")
class GameboardTag(ttag.Tag):
    """
    Tag will ...
    
    Usage:
        {% gameboard 'my_game_name' %}
    
    """
    game = ttag.Arg()    
 
    def render(self, context):        
        data = self.resolve(context)  
        game = data['game']
        #game_dir = "/%s%s/" % (settings.ARCADE_URL, game)
        url = "%s/%s/game.html" % (settings.ARCADE_PATH, game)
        text = open(url, 'rb').read()
        t = Template(text)
        c = Context({ 'STATIC_URL' : '/static/' })
        return t.render(c)


def _strip_quotes(arg):
    if not (arg[0] == arg[-1] and arg[0] in ('"', "'")):
        raise template.TemplateSyntaxError("Argument %s should be in quotes" % arg)
    return arg[1:-1]

