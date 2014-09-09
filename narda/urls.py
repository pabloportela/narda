from django.conf.urls import patterns, include, url

from frontend import views
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    '',
    url('', include('social.apps.django_app.urls', namespace='social')),
    url('', include('django.contrib.auth.urls', namespace='auth')),
    url('', include('frontend.urls')),

    url(r'^social/',
        include('social.apps.django_app.urls', namespace='social')),

    # homepage
    url(r'^$', views.index, name='index'),

    # specific meal. eg. kitchen/johnskitchen/2014-08-11/12/35
    url(r'^kitchen/(?P<kitchen_slug>[\w\-]*)/(?P<meal_datetime>\d{4}-\d{2}-\d{2}/\d{2}/\d{2})/$',
        views.kitchen_detail,
        name='kitchen_detail'),

    # specific meal with number of guests. eg. kitchen/johnskitchen/2014-08-11/12/35
    url(r'^kitchen/(?P<kitchen_slug>[\w\-]*)/(?P<meal_datetime>\d{4}-\d{2}-\d{2}/\d{2}/\d{2})/guests/(?P<number_of_guests>\d{1})/$',
        views.kitchen_detail,
        name='kitchen_detail'),

    # eg. search/date/2014-09-17/guests/4
    url(r'^search/date/(?P<date>\d{4}-\d{2}-\d{2})/guests/(?P<number_of_guests>\d{1})/$',
        views.search,
        name='search'),

    # eg. book/
    url(r'^book/$', views.book, name='book'),

    # backoffice
    url(r'^loudadmin/', include(admin.site.urls)),

    # site info
    url(r'^(?P<content>(why|how_it_works|pricing|faq))/$', views.site_info, name='site_info'),

    #my meals
    url(r'^my_meals/$', views.my_meals, name='my_meals'),
)
