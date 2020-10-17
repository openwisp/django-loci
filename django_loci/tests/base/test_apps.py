from unittest.mock import patch

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase


class BaseTestApps(TestCase):
    app = 'django_loci'

    @patch('django_loci.apps.geocode', return_value=None)
    def test_geocode_strict(self, mocked):
        message = (
            'Geocoding service is experiencing issues or is not properly configured'
        )
        loci_app = apps.get_app_config(self.app)
        with patch.object(loci_app.logger, 'exception') as logger:
            with self.assertRaisesMessage(ImproperlyConfigured, message):
                loci_app.ready()
            logger.assert_called_once_with(message)
        mocked.assert_called_once()
