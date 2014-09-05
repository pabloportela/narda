from django.conf.urls import patterns, url

from frontend import views


urlpatterns = patterns(
    '',
    url(
        r'^review/(?P<kitchen_slug>[\w\-]*)/(?P<token>\w*)/$',
        views.post_guest_review,
        name='post_guest_review'
    ),
)
