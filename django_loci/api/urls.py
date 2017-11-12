from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^api/mobile-location/CONTENT-TYPE/(?P<pk>[^/]+)/$',
        views.mobile_location,
        name='api_mobile_location'),
]
