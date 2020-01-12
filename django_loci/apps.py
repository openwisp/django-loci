import logging

from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _

from .base.geocoding_views import geocode
from .channels.receivers import load_location_receivers
from .settings import DJANGO_LOCI_GEOCODE_STRICT_TEST


class LociConfig(AppConfig):
    name = 'django_loci'
    verbose_name = _('django-loci')
    logger = logging.getLogger(__name__)

    def __setmodels__(self):
        """
        this method can be overridden in 3rd party apps
        """
        from .models import Location
        self.location_model = Location

    def _test_geocoder(self):
        message = 'Geocoding service is experiencing issues or is not properly configured'
        location = geocode('Red Square')
        if location is None:
            if DJANGO_LOCI_GEOCODE_STRICT_TEST:
                raise ImproperlyConfigured(message)
            self.logger.exception(message)

    def ready(self):
        import leaflet
        leaflet.app_settings['NO_GLOBALS'] = False
        self.__setmodels__()
        self._load_receivers()
        self._test_geocoder()

    def _load_receivers(self):
        load_location_receivers(sender=self.location_model)
