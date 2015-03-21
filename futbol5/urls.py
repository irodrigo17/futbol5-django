"""
Django URLs for futbol5 project.
"""

from django.conf.urls import patterns, include, url
from django.contrib import admin


urlpatterns = patterns('',
    url(r'^', include('core.urls', namespace='core')),
    url(r'^admin/', include(admin.site.urls)),
)
