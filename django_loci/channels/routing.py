from .consumers import LocationBroadcast

channel_routing = [
    LocationBroadcast.as_route(path=r'^/loci/location/(?P<pk>[^/]+)/$'),
]
