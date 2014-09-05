from django.conf.urls import patterns, include, url

from frontend import views
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # 3rd party authentication
    url('', include('social.apps.django_app.urls', namespace='social')),
    url('', include('django.contrib.auth.urls', namespace='auth')),
    url(r'^social/', include('social.apps.django_app.urls', namespace='social')),

    # homepage
    url(r'^$', views.index, name='index'),

    # eg. kitchen/johnskitchen/2014-08-11/12:35
    url(
        r'^kitchen/(?P<kitchen_slug>[\w\-]*)/(?P<date>\d{4}-\d{2}-\d{2})/(?P<hour>\d{2})/(?P<minute>\d{2})/$',
        views.kitchen_detail,
        name='kitchen_detail'),

    # eg. search/date/2014-09-17/
    url(r'^search/date/(?P<date>\d{4}-\d{2}-\d{2})/$',
        views.search, name='search'),

    # eg. book/123123
    url(r'^book/$', views.book, name='book'),

    # backoffice
    url(r'^loudadmin/', include(admin.site.urls)),

    # site info
    url(r'^(?P<content>(why|how_it_works|pricing|faq))/$', views.site_info, name='site_info'),

    #my meals
    url(r'^my_meals/$', views.my_meals, name='my_meals'),
)
