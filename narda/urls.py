from django.conf.urls import patterns, include, url

from frontend import views
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^loudadmin/', include(admin.site.urls)),
)
