from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',    
	url(r'^admin/',                include(admin.site.urls)),
    url(r'^game/$', 		       'example.views.somegame'),
    
    url(r'',                include('arcade.urls')),


    
    # Deck
    url(r'^deck/', include('deck.urls')),
)
