import logging

from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _

from . import settings as app_settings
from .base.geocoding_views import geocode
from .channels.receivers import load_location_receivers

logger = logging.getLogger(__name__)


class LociConfig(AppConfig):
    name = 'django_loci'
    verbose_name = _('django-loci')

    def __setmodels__(self):
        """
        this method can be overridden in 3rd party apps
        """
        from .models import Location

        self.location_model = Location

    def _test_geocoding(self):
        # do not run check during development, testing or if feature is disabled
        if (
            settings.DEBUG
            or not app_settings.DJANGO_LOCI_GEOCODE_STRICT_TEST
            or getattr(settings, 'TESTING', False)
        ):
            return
        location = geocode('Red Square')
        if location is None:
            message = (
                'Geocoding service is experiencing issues or is not properly configured'
            )
            logger.exception(message)
            raise ImproperlyConfigured(message)

    def ready(self):
        import leaflet

        leaflet.app_settings['NO_GLOBALS'] = False
        self.__setmodels__()
        self._load_receivers()
        self._test_geocoding()

    def _load_receivers(self):
        load_location_receivers(sender=self.location_model)
