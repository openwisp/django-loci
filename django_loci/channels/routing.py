from channels.routing import route

from .consumers import ws_add, ws_disconnect

channel_routing = [
    route('websocket.connect', ws_add, path=r'^/geo/mobile-location/(?P<pk>[^/]+)/$'),
    route('websocket.disconnect', ws_disconnect, path=r'^/geo/mobile-location/(?P<pk>[^/]+)/$'),
]
