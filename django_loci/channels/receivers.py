from channels import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from ..models import Location


@receiver(post_save, sender=Location, dispatch_uid='ws_update_mobile_location')
def update_mobile_location(sender, instance, **kwargs):
    if not kwargs.get('created') and instance.geometry:
        group_name = 'loci.mobile-location.{0}'.format(str(instance.pk))
        message = {'text': instance.geometry.geojson}
        Group(group_name).send(message, immediately=True)
