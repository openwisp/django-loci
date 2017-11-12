from channels import Group
from channels.security.websockets import allowed_hosts_only
from channels.auth import channel_session_user_from_http
from django.core.exceptions import ValidationError

from ..models import Location


def get_object_or_false(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except (ValidationError, model.DoesNotExist):
        return


@channel_session_user_from_http
def ws_add(message, pk):
    location = get_object_or_false(Location, pk=pk)
    if not location:
        message.reply_channel.send({'close': True})
        return
    org_id = (location.organization_id,)
    user = message.user
    if user.is_authenticated() and (user.is_superuser or org_id in list(user.organizations_pk)):
        content = {'accept': True}
    else:
        content = {'close': True}
    message.reply_channel.send(content)
    Group('geo.mobile-location.{0}'.format(pk)).add(message.reply_channel)


def ws_disconnect(message, pk):
    Group('geo.mobile-location.{0}'.format(pk)).discard(message.reply_channel)
