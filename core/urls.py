from django.conf.urls import patterns, url, include
from core import views, api


urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^matches/(?P<match_id>\d+)/$', views.match, name='match'),
    url(r'^matches/(?P<match_id>\d+)/join/(?P<player_id>\d+)/$', views.join_match, name='join_match'),
    url(r'^matches/(?P<match_id>\d+)/leave/(?P<player_id>\d+)/$', views.leave_match, name='leave_match'),
    url(r'^matches/(?P<match_id>\d+)/addguest/$', views.add_guest, name='add_guest'),
    url(r'^sendmail/$', views.send_mail, name='send_mail'),
    # Wire up our API using automatic URL routing.
    # Additionally, we include login URLs for the browsable API.
    url(r'^api/', include(api.router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
)
