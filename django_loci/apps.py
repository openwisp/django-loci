from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class LociConfig(AppConfig):
    name = 'django_loci'
    verbose_name = _('django-loci')

    def ready(self):
        import leaflet
        leaflet.app_settings['NO_GLOBALS'] = False
        self.load_receivers()

    def load_receivers(self):
        from .channels import receivers  # noqa
