from django.conf.urls import patterns, include, url

from frontend import views
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url('', include('social.apps.django_app.urls', namespace='social')),
    url('', include('django.contrib.auth.urls', namespace='auth')),
    url(r'^social/', include('social.apps.django_app.urls', namespace='social')),

    url(r'^$', views.index, name='index'),
    
    # eg. chef/45/
    url(r'^chef/(?P<chef_id>\d+)/$',views.chef_detail,name='chef'),

    # eg. search/date/2014-09-17/
    url(r'^search/date/(?P<date>\d{4}-\d{2}-\d{2})/$',views.search,name='search'),

    url(r'^loudadmin/', include(admin.site.urls)),

    # 3rd party authentication
    url('', include('social.apps.django_app.urls', namespace='social')),
)
