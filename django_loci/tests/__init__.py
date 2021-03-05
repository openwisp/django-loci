"""
Reusable test helpers
"""
import os

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile


class TestLociMixin(object):
    _object_kwargs = dict(name='test-object')
    _floorplan_path = os.path.join(settings.MEDIA_ROOT, 'floorplan.jpg')

    def tearDown(self):
        if not hasattr(self, 'floorplan_model'):
            return
        for fl in self.floorplan_model.objects.all():
            fl.objectlocation_set.all().delete()
            fl.delete()

    def _create_object(self, **kwargs):
        self._object_kwargs.update(kwargs)
        return self.object_model.objects.create(**self._object_kwargs)

    def _create_location(self, **kwargs):
        options = dict(
            name='test-location',
            address='Via del Corso, Roma, Italia',
            geometry='SRID=4326;POINT (12.512124 41.898903)',
            type='outdoor',
        )
        options.update(kwargs)
        location = self.location_model(**options)
        location.full_clean()
        location.save()
        return location

    def _get_simpleuploadedfile(self):
        with open(self._floorplan_path, 'rb') as f:
            image = f.read()
        return SimpleUploadedFile(
            name='floorplan.jpg', content=image, content_type='image/jpeg'
        )

    def _create_floorplan(self, **kwargs):
        options = dict(floor=1)
        options.update(kwargs)
        if 'image' not in options:
            options['image'] = self._get_simpleuploadedfile()
        if 'location' not in options:
            options['location'] = self._create_location(type='indoor')
        fl = self.floorplan_model(**options)
        fl.full_clean()
        fl.save()
        return fl

    def _create_object_location(self, **kwargs):
        options = {}
        options.update(**kwargs)
        if 'content_object' not in options:
            options['content_object'] = self._create_object()
        if 'location' not in options:
            options['location'] = self._create_location()
        elif options['location'].type == 'indoor':
            options['indoor'] = '-140.38620,40.369227'
        ol = self.object_location_model(**options)
        ol.full_clean()
        ol.save()
        return ol


class TestAdminMixin(object):
    @property
    def url_prefix(self):
        return 'admin:{0}'.format(self.location_model._meta.app_label)

    @property
    def object_url_prefix(self):
        return 'admin:{0}'.format(self.object_model._meta.app_label)

    def _create_admin(self):
        return self.user_model.objects.create_superuser(
            username='admin', password='admin', email='admin@email.org'
        )

    def _login_as_admin(self):
        admin = self._create_admin()
        self.client.force_login(admin)
        return admin

    def _load_content(self, file):
        d = os.path.dirname(os.path.abspath(__file__))
        return open(os.path.join(d, file)).read()
