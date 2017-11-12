from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class LociConfig(AppConfig):
    name = 'django_loci'
    verbose_name = _('django-loci')

    def ready(self):
        import leaflet
        leaflet.app_settings['NO_GLOBALS'] = False
        from .channels import receivers  # noqa
