from channels import Group
from channels.generic.websockets import WebsocketConsumer
from django.core.exceptions import ValidationError

from ..models import Location


def _get_object_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except (ValidationError, model.DoesNotExist):
        return None


class LocationBroadcast(WebsocketConsumer):
    """
    Notifies that the coordinates of a location have changed
    to authorized users (superusers or organization operators)
    """
    http_user = True
    model = Location

    def connect(self, message, pk):
        location = _get_object_or_none(self.model, pk=pk)
        if not location or not self.is_authorized(message.user, location):
            message.reply_channel.send({'close': True})
            return
        message.reply_channel.send({'accept': True})
        Group('geo.mobile-location.{0}'.format(pk)).add(message.reply_channel)

    def is_authorized(self, user, location):
        return user.is_authenticated() and user.is_staff

    def disconnect(self, message, pk):
        """
        Perform things on connection close
        """
        Group('geo.mobile-location.{0}'.format(pk)).discard(message.reply_channel)
