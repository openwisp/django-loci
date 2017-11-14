from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from openwisp_utils.base import TimeStampedEditableModel


@python_2_unicode_compatible
class Device(TimeStampedEditableModel):
    name = models.CharField(_('name'), max_length=75)

    def __str__(self):
        return self.name
