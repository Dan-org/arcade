from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib import admin

import arcade.sdjango
arcade.sdjango.autodiscover()

#admin.autodiscover()

urlpatterns = patterns('',
    
	#url(r'^admin/',                        include(admin.site.urls)),
    #url(r'^playpolitics/$', 		       TemplateView.as_view(template_name='playpolitics/index.html')),
    #url(r'^playpolitics/stateofnature/$',  'example.views.stateofnature', name="stateofnature"),
    url("^socket\.io",                      include(arcade.sdjango.urls)),
)
