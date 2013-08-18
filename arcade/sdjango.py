import logging

from socketio import socketio_manage
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.importlib import import_module

import os
from os.path import abspath, basename, dirname, join, normpath, exists

import imp, sys
from django.conf import settings

# for Django 1.3 support
try:
    from django.conf.urls import patterns, url, include
except ImportError:
    from django.conf.urls.defaults import patterns, url, include


SOCKETIO_NS = {}


LOADING_SOCKETIO = False


def autodiscover():
    """
    Auto-discover INSTALLED_APPS sockets.py modules and fail silently when
    not present. NOTE: socketio_autodiscover was inspired/copied from
    django.contrib.admin autodiscover
    """
    global LOADING_SOCKETIO
    if LOADING_SOCKETIO:
        return
    LOADING_SOCKETIO = True

    
    arcade_base = os.path.basename(settings.ARCADE_PATH)
    import_module(arcade_base)
    print "arcade at: %s" % settings.ARCADE_PATH
    for game in os.walk("%s" % settings.ARCADE_PATH).next()[1]:  #all the subdirs of ARCADE_DIR
        game_path = "%s/%s" % (settings.ARCADE_PATH, game)        
        try:
            imp.find_module('sockets', [game_path])     
            print "found: %s" % game        
        except ImportError:   
            print "couldn't import: %s" % game
            continue
        import_module("%s.%s.%s" % (arcade_base, game, 'sockets'))

    LOADING_SOCKETIO = False



class namespace(object):
    def __init__(self, name=''):
        self.name = name
 
    def __call__(self, handler):
        SOCKETIO_NS[self.name] = handler
        return handler



@csrf_exempt
def socketio(request):
    try:
        socketio_manage(request.environ, SOCKETIO_NS, request)
    except:
        logging.getLogger("socketio").error("Exception while handling socketio connection", exc_info=True)
    return HttpResponse("")


urls = patterns("", (r'', socketio))