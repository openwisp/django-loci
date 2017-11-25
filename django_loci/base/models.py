import logging
import os

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models
from django.contrib.humanize.templatetags.humanize import ordinal
from django.core.exceptions import ValidationError
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from openwisp_utils.base import TimeStampedEditableModel

from .. import settings as app_settings

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class AbstractLocation(TimeStampedEditableModel):
    LOCATION_TYPES = (
        ('outdoor', _('Outdoor environment (eg: street, square, garden, land)')),
        ('indoor', _('Indoor environment (eg: building, roofs, subway, large vehicles)')),
    )
    name = models.CharField(_('name'), max_length=75,
                            help_text=_('A descriptive name of the location '
                                        '(building name, company name, etc.)'))
    type = models.CharField(choices=LOCATION_TYPES, max_length=8, db_index=True,
                            help_text=_('indoor locations can have floorplans associated to them'))
    is_mobile = models.BooleanField(_('is mobile?'), default=False, db_index=True,
                                    help_text=_('is this location a moving object?'))
    address = models.CharField(_('address'), db_index=True,
                               max_length=256, blank=True)
    geometry = models.GeometryField(_('geometry'), blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def clean(self):
        self._validate_outdoor_floorplans()

    def _validate_outdoor_floorplans(self):
        """
        if a location type is changed from indoor to outdoor
        but the location has still floorplan associated to it,
        a ValidationError will be raised
        """
        if self.type == 'indoor' or self._state.adding:
            return
        if self.floorplan_set.count() > 0:
            msg = 'this location has floorplans associated to it, ' \
                  'please delete them before changing its type'
            raise ValidationError({'type': msg})

    @property
    def short_type(self):
        return _(self.type.capitalize())


@python_2_unicode_compatible
class AbstractFloorPlan(TimeStampedEditableModel):
    location = models.ForeignKey('django_loci.Location')
    floor = models.SmallIntegerField(_('floor'))
    image = models.ImageField(_('image'),
                              upload_to=app_settings.FLOORPLAN_STORAGE.upload_to,
                              storage=app_settings.FLOORPLAN_STORAGE(),
                              help_text=_('floor plan image'))

    class Meta:
        abstract = True
        unique_together = ('location', 'floor')

    def __str__(self):
        if self.floor is not 0:
            suffix = _('{0} floor').format(ordinal(self.floor))
        else:
            suffix = _('ground floor')
        return '{0} {1}'.format(self.location.name, suffix)

    def clean(self):
        self._validate_location_type()

    def delete(self, *args, **kwargs):
        super(AbstractFloorPlan, self).delete(*args, **kwargs)
        self._remove_image()

    def _validate_location_type(self):
        if self.location and self.location.type != 'indoor':
            msg = 'floorplans can only be associated '\
                  'to locations of type "indoor"'
            raise ValidationError(msg)

    def _remove_image(self):
        path = self.image.file.name
        if os.path.isfile(path):
            os.remove(path)
        else:
            msg = 'floorplan image not found while deleting {0}: {1}'
            logger.error(msg.format(self, path))


class AbstractObjectLocation(TimeStampedEditableModel):
    LOCATION_TYPES = (
        ('outdoor', _('Outdoor')),
        ('indoor', _('Indoor')),
        ('mobile', _('Mobile')),
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=36, db_index=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    location = models.ForeignKey('django_loci.Location', models.PROTECT,
                                 blank=True, null=True)
    floorplan = models.ForeignKey('django_loci.Floorplan', models.PROTECT,
                                  blank=True, null=True)
    indoor = models.CharField(_('indoor position'), max_length=64,
                              blank=True, null=True)

    class Meta:
        abstract = True
        unique_together = ('content_type', 'object_id')

    def _clean_indoor_location(self):
        """
        ensures related floorplan is not
        associated to a different location
        """
        # skip validation if the instance does not
        # have a floorplan assigned to it yet
        if not self.location or self.location.type != 'indoor' or not self.floorplan:
            return
        if self.location != self.floorplan.location:
            raise ValidationError(_('Invalid floorplan (belongs to a different location)'))

    def _raise_invalid_indoor(self):
        raise ValidationError({'indoor': _('invalid value')})

    def _clean_indoor_position(self):
        """
        ensures invalid indoor position values
        cannot be inserted into the database
        """
        # stop here if location not defined yet
        # (other validation errors will be triggered)
        if not self.location:
            return
        # do not allow non empty values for outdoor locations
        if self.location.type != 'indoor' and self.indoor not in [None, '']:
            self._raise_invalid_indoor()
        # allow empty values for outdoor locations
        elif self.location.type != 'indoor' and self.indoor in [None, '']:
            return
        # split indoor position
        position = []
        if self.indoor:
            position = self.indoor.split(',')
        # must have at least e elements
        if len(position) != 2:
            self._raise_invalid_indoor()
        # each member must be convertible to float
        else:
            for part in position:
                try:
                    float(part)
                except ValueError:
                    self._raise_invalid_indoor()

    def clean(self):
        self._clean_indoor_location()
        self._clean_indoor_position()
