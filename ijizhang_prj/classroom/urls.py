#coding=utf-8
from django.conf.urls import patterns, include, url
from django.contrib import admin


from classroom import views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.index_room),
    url(r'^index_room/', views.index_room, name='index_room'),
    url(r'^room/(?P<pk>\d+)/$', views.detail_room, name='detail_room'),
    url(r'^new_room/',views.new_room,name='new_room'),
    url(r'^edit_room/(?P<pk>\d+)/$', views.edit_room, name='edit_room'),   
    url(r'^join_room/(?P<room_id>\d+)/(?P<add_type>\d+)/$', views.join_room, name='join_room'), 
    url(r'^room/(?P<id>\d+)/comments/$', views.room_comments, name='room_comments'),
    url(r'^room/(?P<id>\d+)/draws/$', views.room_draws, name='room_draws'),   
    url(r'^room/(?P<id>\d+)/clear_draws/$', views.clear_draws, name='clear_draws'),  
    url(r'^room/(?P<id>\d+)/members/$', views.room_members, name='room_members'),       
)
