from unittest.mock import patch

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .. import TestLociMixin


class BaseTestApps(TestLociMixin):
    app = 'django_loci'

    @patch('django_loci.apps.geocode', return_value=None)
    @patch('django_loci.apps.logger.exception')
    @patch.object(settings, 'TESTING', False)
    def test_geocode_strict(self, logger_mocked, geocode_mocked):
        message = (
            'Geocoding service is experiencing issues or is not properly configured'
        )
        loci_app = apps.get_app_config(self.app)
        with self.assertRaisesMessage(ImproperlyConfigured, message):
            loci_app.ready()
        logger_mocked.assert_called_once_with(message)
        geocode_mocked.assert_called_once()
