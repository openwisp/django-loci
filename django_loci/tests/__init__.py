"""
Reusable test helpers
"""


class TestLociMixin(object):
    _object_kwargs = dict(name='test-object')

    def _create_object(self, **kwargs):
        self._object_kwargs.update(kwargs)
        return self.object_model.objects.create(**self._object_kwargs)

    def _create_location(self, **kwargs):
        options = dict(name='test-location',
                       address='Via del Corso, Roma, Italia',
                       geometry='SRID=4326;POINT (12.512124 41.898903)')
        options.update(kwargs)
        location = self.location_model(**options)
        location.full_clean()
        location.save()
        return location

    def _create_floorplan(self, **kwargs):
        options = dict(floor=1,
                       image='floorplan.jpg')
        options.update(kwargs)
        if 'location' not in options:
            options['location'] = self._create_location()
        fl = self.floorplan_model(**options)
        fl.full_clean()
        fl.save()
        return fl

    def _create_object_location(self, **kwargs):
        options = dict(type='outdoor')
        options.update(**kwargs)
        if 'content_object' not in options:
            options['content_object'] = self._create_object()
        if 'location' not in options:
            options['location'] = self._create_location()
        ol = self.object_location_model(**options)
        ol.full_clean()
        ol.save()
        return ol


class TestAdminMixin(object):
    def _create_admin(self):
        return self.user_model.objects.create_superuser(username='admin',
                                                        password='admin',
                                                        email='admin@email.org')

    def _login_as_admin(self):
        admin = self._create_admin()
        self.client.force_login(admin)
        return admin
