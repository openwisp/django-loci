from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from django.urls import path

from django_loci.channels.base import location_broadcast_path
from django_loci.channels.consumers import LocationBroadcast

channel_routing = ProtocolTypeRouter(
    {
        'websocket': AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(
                    [
                        path(
                            location_broadcast_path,
                            LocationBroadcast.as_asgi(),
                            name='LocationChannel',
                        )
                    ]
                )
            )
        ),
        'http': get_asgi_application(),
    }
)
