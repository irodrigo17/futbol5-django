"""
Core app URLs containing views and api URL patterns.
"""

from django.conf.urls import patterns, url, include
from core import views, api


urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^matches/(?P<match_id>\d+)/$', views.match, name='match'),
    url(r'^matches/(?P<match_id>\d+)/join/(?P<player_id>\d+)/$', views.join_match, name='join_match'),
    url(r'^matches/(?P<match_id>\d+)/leave/(?P<player_id>\d+)/$', views.leave_match, name='leave_match'),
    url(r'^matches/(?P<match_id>\d+)/addguest/$', views.add_guest, name='add_guest'),
    url(r'^removeguest/(?P<guest_id>\d+)/$', views.remove_guest, name='remove_guest'),
    url(r'^sendmail/$', views.send_mail, name='send_mail'),
    url(r'^api/', include(api.router.urls, namespace='api')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
)
