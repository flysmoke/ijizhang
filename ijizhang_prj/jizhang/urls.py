#coding=utf-8
from django.conf.urls import patterns, include, url
from django.contrib import admin


from jizhang import views

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', views.index_item, name='index_item'),
	url(r'^index_item/', views.index_item, name='index_item'),
	url(r'^index_category', views.index_category, name='index_category'),
	url(r'^item/(?P<pk>\d+)/$', views.edit_item, name='edit_item'),
	url(r'^category/(?P<pk>\d+)/$', views.edit_category, name='edit_category'),
	url(r'^new_item',views.new_item,name='new_item'),
	url(r'^new_category',views.new_category,name='new_category'),
	url(r'^find_item',views.find_item,name='find_item'),
	url(r'^report_item',views.report_item,name='report_item'),
	url(r'^export_to_item_csv',views.export_to_item_csv,name='export_to_item_csv'),
)
