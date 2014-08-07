from django.conf.urls import patterns, include, url

from frontend import views
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    
    # eg. chef/45/
    url(r'^chef/(?P<chef_id>\d+)/$',views.chef_detail,name='chef'),

    # eg. search/date/2014-09-17/
    url(r'^search/date/(?P<date>\d{4}-\d{2}-\d{2})/$',views.search,name='search'),

    url(r'^loudadmin/', include(admin.site.urls)),
)
