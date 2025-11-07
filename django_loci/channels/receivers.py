import json

import channels.layers
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save
from django.dispatch import receiver


def update_mobile_location(sender, instance, **kwargs):
    if not kwargs.get("created") and instance.geometry:
        group_name = "loci.mobile-location.{0}".format(str(instance.pk))
        channel_layer = channels.layers.get_channel_layer()
        message = {
            "geometry": json.loads(instance.geometry.geojson),
            "address": instance.address,
        }
        async_to_sync(channel_layer.group_send)(
            group_name, {"type": "send_message", "message": message}
        )

def update_mobile_all_locations(sender, instance, **kwargs):
    if not kwargs.get("created") and instance.geometry:
        channel_layer = channels.layers.get_channel_layer()
        group_name = "loci.mobile-location.all"
        message = {
            "id": str(instance.pk),
            "geometry": json.loads(instance.geometry.geojson),
            "address": instance.address,
            "name": instance.name,
            "type": instance.type,
            "is_mobile": instance.is_mobile
        }
        async_to_sync(channel_layer.group_send)(
            group_name, {"type": "send_message", "message": message}
        )


def load_location_receivers(sender):
    """
    enables signal listening when called
    designed to be called in AppConfig subclasses
    """
    # using decorator pattern with old syntax
    # in order to decorate an existing function
    receiver(post_save, sender=sender, dispatch_uid="ws_update_mobile_location")(
        update_mobile_location
    )
    receiver(post_save, sender=sender, dispatch_uid="ws_update_mobile_location_all")(
        update_mobile_all_locations    
    )
