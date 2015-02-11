from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'futbol5.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^', include('core.urls', namespace='core')),
    url(r'^admin/', include(admin.site.urls)),
)