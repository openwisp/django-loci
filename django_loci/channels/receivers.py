import json

import channels.layers
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save
from django.dispatch import receiver


def update_mobile_location(sender, instance, **kwargs):
    """
    Sends WebSocket updates when a location record is updated.
    - Sends a message with the specific location update.
    - Sends a message with the common (all locations) update.
    """
    if not kwargs.get("created") and instance.geometry:
        channel_layer = channels.layers.get_channel_layer()
        specific_location_group_name = f"loci.mobile-location.{instance.pk}"
        specific_location_message = {
            "geometry": json.loads(instance.geometry.geojson),
            "address": instance.address,
        }
        async_to_sync(channel_layer.group_send)(
            specific_location_group_name,
            {"type": "send_message", "message": specific_location_message},
        )
        # Broadcast update to track updates across all locations
        common_location_group_name = "loci.mobile-location.common"
        common_location_message = {
            "id": str(instance.pk),
            "geometry": json.loads(instance.geometry.geojson),
            "address": instance.address,
            "name": instance.name,
            "type": instance.type,
            "is_mobile": instance.is_mobile,
        }
        async_to_sync(channel_layer.group_send)(
            common_location_group_name,
            {"type": "send_message", "message": common_location_message},
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
