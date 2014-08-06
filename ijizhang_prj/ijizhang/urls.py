#coding=utf-8
from django.conf.urls import patterns, include, url
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',
	url(r'^admin/', include(admin.site.urls)),
	url(r'^accounts/',include('accounts.urls',namespace='accounts')),	
	url(r'^jizhang/',include('jizhang.urls',namespace='jizhang')),
	url(r'^$',include('jizhang.urls',namespace='jizhang')),
)

from django.contrib.staticfiles.urls import staticfiles_urlpatterns  
urlpatterns += staticfiles_urlpatterns() 