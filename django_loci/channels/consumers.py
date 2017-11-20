from channels import Group
from channels.auth import channel_session_user_from_http
from django.core.exceptions import ValidationError

from ..models import Location


def _get_object_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except (ValidationError, model.DoesNotExist):
        return None


@channel_session_user_from_http
def ws_add(message, pk):
    location = _get_object_or_none(Location, pk=pk)
    if not location:
        message.reply_channel.send({'close': True})
        return
    check = True
    user = message.user
    if user.is_authenticated() and user.is_staff and (user.is_superuser or check):
        content = {'accept': True}
    else:
        content = {'close': True}
    message.reply_channel.send(content)
    Group('geo.mobile-location.{0}'.format(pk)).add(message.reply_channel)


def ws_disconnect(message, pk):
    Group('geo.mobile-location.{0}'.format(pk)).discard(message.reply_channel)
