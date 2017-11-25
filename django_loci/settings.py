from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

FLOORPLAN_STORAGE = getattr(settings, 'LOCI_FLOORPLAN_STORAGE', 'django_loci.storage.OverwriteStorage')

try:
    FLOORPLAN_STORAGE = import_string(FLOORPLAN_STORAGE)
except ImportError:  # pragma: nocover
    raise ImproperlyConfigured('Import of {0} failed'.format(FLOORPLAN_STORAGE))
