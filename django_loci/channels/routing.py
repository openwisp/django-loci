from .consumers import LocationBroadcast

channel_routing = [
    LocationBroadcast.as_route(path=r'^/geo/mobile-location/(?P<pk>[^/]+)/$'),
]
