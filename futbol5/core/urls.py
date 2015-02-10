from django.conf.urls import patterns, url
from core import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^matches/(?P<match_id>\d+)/$', views.match, name='match'),
    url(r'^matches/(?P<match_id>\d+)/join/(?P<player_id>\d+)/$', views.join_match, name='join_match'),
    url(r'^matches/(?P<match_id>\d+)/leave/(?P<player_id>\d+)/$', views.leave_match, name='leave_match'),
)
