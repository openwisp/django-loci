from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from django.core.exceptions import ValidationError

location_broadcast_path = 'ws/loci/location/<uuid:pk>/'


def _get_object_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except (ValidationError, model.DoesNotExist):
        return None


class BaseLocationBroadcast(JsonWebsocketConsumer):
    """
    Notifies that the coordinates of a location have changed
    to authorized users (superusers or organization operators)
    """

    http_user = True

    def connect(self):
        self.pk = None
        try:
            user = self.scope['user']
            self.pk = self.scope['url_route']['kwargs']['pk']
        except KeyError:
            # Will fall here when the scope does not have
            # one of the variables, most commonly, user
            # (When a user tries to access without loggin in)
            self.close()
        location = _get_object_or_none(self.model, pk=self.pk)
        if not location or not self.is_authorized(user, location):
            self.close()
            return
        self.accept()
        async_to_sync(self.channel_layer.group_add)(
            'loci.mobile-location.{0}'.format(self.pk), self.channel_name
        )

    def is_authorized(self, user, location):
        perm = '{0}.change_location'.format(self.model._meta.app_label)
        authenticated = user.is_authenticated
        return authenticated and (
            user.is_superuser or (user.is_staff and user.has_perm(perm))
        )

    def send_message(self, event):
        self.send_json(event['message'])

    def disconnect(self, message=None):
        """
        Perform things on connection close
        """
        async_to_sync(self.channel_layer.group_discard)(
            'loci.mobile-location.{0}'.format(self.pk), self.channel_name
        )
