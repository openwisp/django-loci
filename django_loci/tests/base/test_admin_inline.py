from django.contrib.gis.geos import GEOSGeometry
from django.db.models.fields.files import ImageFieldFile
from django.urls import reverse

from .. import TestAdminMixin, TestLociMixin


class BaseTestAdminInline(TestAdminMixin, TestLociMixin):
    @classmethod
    def _get_prefix(cls):
        s = '{0}-{1}-content_type-object_id'
        return s.format(
            cls.location_model._meta.app_label,
            cls.object_location_model.__name__.lower(),
        )

    @classmethod
    def _get_params(cls):
        _p = cls._get_prefix()
        return {
            '{0}-0-is_mobile'.format(_p): False,
            '{0}-0-name'.format(_p): 'Centro Piazza Venezia',
            '{0}-0-address'.format(_p): 'Piazza Venezia, Roma, Italia',
            '{0}-0-geometry'.format(
                _p
            ): '{"type": "Point", "coordinates": [12.512124, 41.898903]}',
            '{0}-TOTAL_FORMS'.format(_p): '1',
            '{0}-INITIAL_FORMS'.format(_p): '0',
            '{0}-MIN_NUM_FORMS'.format(_p): '0',
            '{0}-MAX_NUM_FORMS'.format(_p): '1',
        }

    @property
    def params(self):
        return self.__class__._get_params()

    def _get_url_prefix(self):
        return '{0}_{1}'.format(
            self.object_url_prefix, self.object_model.__name__.lower()
        )

    @property
    def add_url(self):
        return '{0}_add'.format(self._get_url_prefix())

    @property
    def change_url(self):
        return '{0}_change'.format(self._get_url_prefix())

    def test_json_urls(self):
        self._login_as_admin()
        r = self.client.get(reverse(self.add_url))
        url = reverse('admin:django_loci_location_json', args=['0000'])
        self.assertContains(r, url)
        url = reverse('admin:django_loci_location_floorplans_json', args=['0000'])
        self.assertContains(r, url)

    def test_add_outdoor_new(self):
        self._login_as_admin()
        p = self._get_prefix()
        params = self.params
        params.update(
            {
                'name': 'test-outdoor-add-new',
                '{0}-0-type'.format(p): 'outdoor',
                '{0}-0-location_selection'.format(p): 'new',
                '{0}-0-location'.format(p): '',
                '{0}-0-floorplan_selection'.format(p): '',
                '{0}-0-floorplan'.format(p): '',
                '{0}-0-floor'.format(p): '',
                '{0}-0-image'.format(p): '',
                '{0}-0-indoor'.format(p): '',
                '{0}-0-id'.format(p): '',
            }
        )
        r = self.client.post(reverse(self.add_url), params, follow=True)
        self.assertNotContains(r, 'errors')
        loc = self.location_model.objects.get(name=params['{0}-0-name'.format(p)])
        self.assertEqual(loc.address, params['{0}-0-address'.format(p)])
        self.assertEqual(
            loc.geometry.coords, GEOSGeometry(params['{0}-0-geometry'.format(p)]).coords
        )
        self.assertEqual(loc.objectlocation_set.count(), 1)
        self.assertEqual(
            loc.objectlocation_set.first().content_object.name, params['name']
        )

    def test_add_outdoor_existing(self):
        self._login_as_admin()
        p = self._get_prefix()
        pre_loc = self._create_location()
        params = self.params
        params.update(
            {
                'name': 'test-outdoor-add-existing',
                '{0}-0-type'.format(p): 'outdoor',
                '{0}-0-location_selection'.format(p): 'existing',
                '{0}-0-location'.format(p): pre_loc.id,
                '{0}-0-floorplan_selection'.format(p): '',
                '{0}-0-floorplan'.format(p): '',
                '{0}-0-floor'.format(p): '',
                '{0}-0-image'.format(p): '',
                '{0}-0-indoor'.format(p): '',
                '{0}-0-id'.format(p): '',
            }
        )
        r = self.client.post(reverse(self.add_url), params, follow=True)
        self.assertNotContains(r, 'errors')
        loc = self.location_model.objects.get(name=params['{0}-0-name'.format(p)])
        self.assertEqual(pre_loc.id, loc.id)
        self.assertEqual(loc.address, params['{0}-0-address'.format(p)])
        self.assertEqual(
            loc.geometry.coords, GEOSGeometry(params['{0}-0-geometry'.format(p)]).coords
        )
        self.assertEqual(loc.objectlocation_set.count(), 1)
        self.assertEqual(
            loc.objectlocation_set.first().content_object.name, params['name']
        )
        self.assertEqual(self.location_model.objects.count(), 1)

    def test_change_outdoor(self):
        self._login_as_admin()
        p = self._get_prefix()
        obj = self._create_object(name='test-change-outdoor')
        pre_loc = self._create_location()
        ol = self._create_object_location(location=pre_loc, content_object=obj)
        # -- ensure change form doesn't raise any exception
        r = self.client.get(reverse(self.change_url, args=[obj.pk]))
        self.assertContains(r, obj.name)
        # -- post changes
        params = self.params
        params.update(
            {
                'name': obj.name,
                '{0}-0-type'.format(p): 'outdoor',
                '{0}-0-location_selection'.format(p): 'existing',
                '{0}-0-location'.format(p): pre_loc.id,
                '{0}-0-floorplan_selection'.format(p): '',
                '{0}-0-floorplan'.format(p): '',
                '{0}-0-floor'.format(p): '',
                '{0}-0-image'.format(p): '',
                '{0}-0-indoor'.format(p): '',
                '{0}-0-id'.format(p): ol.id,
                '{0}-INITIAL_FORMS'.format(p): '1',
            }
        )
        r = self.client.post(
            reverse(self.change_url, args=[obj.pk]), params, follow=True
        )
        self.assertNotContains(r, 'errors')
        loc = self.location_model.objects.get(name=params['{0}-0-name'.format(p)])
        self.assertEqual(pre_loc.id, loc.id)
        self.assertEqual(loc.address, params['{0}-0-address'.format(p)])
        self.assertEqual(
            loc.geometry.coords, GEOSGeometry(params['{0}-0-geometry'.format(p)]).coords
        )
        self.assertEqual(loc.objectlocation_set.count(), 1)
        self.assertEqual(
            loc.objectlocation_set.first().content_object.name, params['name']
        )
        self.assertEqual(self.location_model.objects.count(), 1)

    def test_change_outdoor_to_different_location(self):
        self._login_as_admin()
        p = self._get_prefix()
        ol = self._create_object_location()
        new_loc = self._create_location(
            name='different-location',
            address='Piazza Venezia, Roma, Italia',
            geometry='SRID=4326;POINT (12.512324 41.898703)',
        )
        # -- post changes
        params = self.params
        changed_name = '{0} changed'.format(new_loc.name)
        params.update(
            {
                'name': 'test-outdoor-change-different',
                '{0}-0-type'.format(p): 'outdoor',
                '{0}-0-location_selection'.format(p): 'existing',
                '{0}-0-location'.format(p): new_loc.id,
                '{0}-0-name'.format(p): changed_name,
                '{0}-0-address'.format(p): new_loc.address,
                '{0}-0-geometry'.format(p): new_loc.geometry.geojson,
                '{0}-0-floorplan_selection'.format(p): '',
                '{0}-0-floorplan'.format(p): '',
                '{0}-0-floor'.format(p): '',
                '{0}-0-image'.format(p): '',
                '{0}-0-indoor'.format(p): '',
                '{0}-0-id'.format(p): ol.id,
                '{0}-INITIAL_FORMS'.format(p): '1',
            }
        )
        r = self.client.post(
            reverse(self.change_url, args=[ol.content_object.pk]), params, follow=True
        )
        self.assertNotContains(r, 'errors')
        loc = self.location_model.objects.get(name=changed_name)
        self.assertEqual(new_loc.id, loc.id)
        self.assertEqual(loc.address, params['{0}-0-address'.format(p)])
        self.assertEqual(
            loc.geometry.coords, GEOSGeometry(params['{0}-0-geometry'.format(p)]).coords
        )
        self.assertEqual(loc.objectlocation_set.count(), 1)
        self.assertEqual(
            loc.objectlocation_set.first().content_object.name, params['name']
        )
        self.assertEqual(self.location_model.objects.count(), 2)

    def test_add_indoor_new_location_new_floorplan(self):
        self._login_as_admin()
        p = self._get_prefix()
        params = self.params
        floorplan_file = open(self._floorplan_path, 'rb')
        params.update(
            {
                'name': 'test-add-indoor-new-location-new-floorplan',
                '{0}-0-type'.format(p): 'indoor',
                '{0}-0-location_selection'.format(p): 'new',
                '{0}-0-location'.format(p): '',
                '{0}-0-floorplan_selection'.format(p): 'new',
                '{0}-0-floorplan'.format(p): '',
                '{0}-0-floor'.format(p): '1',
                '{0}-0-image'.format(p): floorplan_file,
                '{0}-0-indoor'.format(p): '-100,100',
                '{0}-0-id'.format(p): '',
            }
        )
        r = self.client.post(reverse(self.add_url), params, follow=True)
        floorplan_file.close()
        self.assertNotContains(r, 'errors')
        loc = self.location_model.objects.get(name=params['{0}-0-name'.format(p)])
        self.assertEqual(loc.address, params['{0}-0-address'.format(p)])
        self.assertEqual(
            loc.geometry.coords, GEOSGeometry(params['{0}-0-geometry'.format(p)]).coords
        )
        self.assertEqual(loc.objectlocation_set.count(), 1)
        self.assertEqual(self.location_model.objects.count(), 1)
        self.assertEqual(self.floorplan_model.objects.count(), 1)
        ol = loc.objectlocation_set.first()
        self.assertEqual(ol.content_object.name, params['name'])
        self.assertEqual(ol.location.type, 'indoor')
        self.assertEqual(ol.floorplan.floor, 1)
        self.assertIsInstance(ol.floorplan.image, ImageFieldFile)
        self.assertEqual(ol.indoor, '-100,100')

    def test_add_indoor_existing_location_new_floorplan(self):
        self._login_as_admin()
        pre_loc = self._create_location(type='indoor')
        p = self._get_prefix()
        params = self.params
        floorplan_file = open(self._floorplan_path, 'rb')
        name = 'test-add-indoor-existing-location-new-floorplan'
        params.update(
            {
                'name': name,
                '{0}-0-type'.format(p): 'indoor',
                '{0}-0-location_selection'.format(p): 'existing',
                '{0}-0-location'.format(p): pre_loc.id,
                '{0}-0-name'.format(p): pre_loc.name,
                '{0}-0-address'.format(p): pre_loc.address,
                '{0}-0-geometry'.format(p): pre_loc.geometry.geojson,
                '{0}-0-floorplan_selection'.format(p): 'new',
                '{0}-0-floorplan'.format(p): '',
                '{0}-0-floor'.format(p): '0',
                '{0}-0-image'.format(p): floorplan_file,
                '{0}-0-indoor'.format(p): '-100,100',
                '{0}-0-id'.format(p): '',
            }
        )
        r = self.client.post(reverse(self.add_url), params, follow=True)
        floorplan_file.close()
        # with open('test.html', 'w') as f:
        #     f.write(r.content.decode())
        self.assertNotContains(r, 'errors')
        loc = self.location_model.objects.get(name=params['{0}-0-name'.format(p)])
        self.assertEqual(loc.address, params['{0}-0-address'.format(p)])
        self.assertEqual(
            loc.geometry.coords, GEOSGeometry(params['{0}-0-geometry'.format(p)]).coords
        )
        self.assertEqual(loc.objectlocation_set.count(), 1)
        self.assertEqual(self.location_model.objects.count(), 1)
        self.assertEqual(self.floorplan_model.objects.count(), 1)
        ol = loc.objectlocation_set.first()
        self.assertEqual(ol.content_object.name, params['name'])
        self.assertEqual(ol.location.type, 'indoor')
        self.assertEqual(ol.floorplan.floor, 0)
        self.assertIsInstance(ol.floorplan.image, ImageFieldFile)
        self.assertEqual(ol.indoor, '-100,100')

    def test_add_indoor_existing_location_existing_floorplan(self):
        self._login_as_admin()
        pre_loc = self._create_location(type='indoor')
        pre_fl = self._create_floorplan(location=pre_loc, floor=2)
        p = self._get_prefix()
        params = self.params
        name = 'test-add-indoor-existing-location-new-floorplan'
        params.update(
            {
                'name': name,
                '{0}-0-type'.format(p): 'indoor',
                '{0}-0-location_selection'.format(p): 'existing',
                '{0}-0-location'.format(p): pre_loc.id,
                '{0}-0-name'.format(p): name,
                '{0}-0-address'.format(p): pre_loc.address,
                '{0}-0-location-geometry'.format(p): pre_loc.geometry,
                '{0}-0-floorplan_selection'.format(p): 'existing',
                '{0}-0-floorplan'.format(p): pre_fl.id,
                '{0}-0-floor'.format(p): 3,  # floor
                '{0}-0-image'.format(p): '',
                '{0}-0-indoor'.format(p): '-110,110',
                '{0}-0-id'.format(p): '',
            }
        )
        r = self.client.post(reverse(self.add_url), params, follow=True)
        self.assertNotContains(r, 'errors')
        loc = self.location_model.objects.get(name=name)
        self.assertEqual(loc.id, pre_loc.id)
        self.assertEqual(loc.address, params['{0}-0-address'.format(p)])
        self.assertEqual(
            loc.geometry.coords, GEOSGeometry(params['{0}-0-geometry'.format(p)]).coords
        )
        self.assertEqual(loc.objectlocation_set.count(), 1)
        self.assertEqual(self.location_model.objects.count(), 1)
        self.assertEqual(self.floorplan_model.objects.count(), 1)
        ol = loc.objectlocation_set.first()
        self.assertEqual(ol.content_object.name, params['name'])
        self.assertEqual(ol.location.type, 'indoor')
        self.assertEqual(ol.floorplan.id, pre_fl.id)
        self.assertEqual(ol.floorplan.floor, 3)
        self.assertIsInstance(ol.floorplan.image, ImageFieldFile)
        self.assertEqual(ol.indoor, '-110,110')

    def test_change_indoor(self):
        self._login_as_admin()
        p = self._get_prefix()
        obj = self._create_object(name='test-change-indoor')
        pre_loc = self._create_location(type='indoor')
        pre_fl = self._create_floorplan(location=pre_loc)
        ol = self._create_object_location(
            content_object=obj, location=pre_loc, floorplan=pre_fl, indoor='-100,100'
        )
        # -- ensure change form doesn't raise any exception
        r = self.client.get(reverse(self.change_url, args=[obj.pk]))
        self.assertContains(r, obj.name)
        # -- post changes
        params = self.params
        floorplan_file = open(self._floorplan_path, 'rb')
        changed_name = '{0} changed'.format(pre_loc.name)
        params.update(
            {
                'name': obj.name,
                '{0}-0-type'.format(p): 'indoor',
                '{0}-0-location_selection'.format(p): 'existing',
                '{0}-0-location'.format(p): pre_loc.id,
                '{0}-0-name'.format(p): changed_name,
                '{0}-0-address'.format(p): 'changed-address',
                '{0}-0-location-geometry'.format(p): pre_loc.geometry,
                '{0}-0-floorplan_selection'.format(p): 'existing',
                '{0}-0-floorplan'.format(p): pre_fl.id,
                '{0}-0-floor'.format(p): 3,  # floor
                '{0}-0-image'.format(p): floorplan_file,
                '{0}-0-indoor'.format(p): '-110,110',
                '{0}-0-id'.format(p): ol.id,
                '{0}-INITIAL_FORMS'.format(p): '1',
            }
        )
        r = self.client.post(
            reverse(self.change_url, args=[obj.pk]), params, follow=True
        )
        floorplan_file.close()
        self.assertNotContains(r, 'errors')
        loc = self.location_model.objects.get(name=changed_name)
        self.assertEqual(loc.id, pre_loc.id)
        self.assertEqual(loc.address, 'changed-address')
        self.assertEqual(
            loc.geometry.coords, GEOSGeometry(params['{0}-0-geometry'.format(p)]).coords
        )
        self.assertEqual(loc.objectlocation_set.count(), 1)
        self.assertEqual(self.location_model.objects.count(), 1)
        self.assertEqual(self.floorplan_model.objects.count(), 1)
        ol = loc.objectlocation_set.first()
        self.assertEqual(ol.content_object.name, params['name'])
        self.assertEqual(ol.location.type, 'indoor')
        self.assertEqual(ol.floorplan.id, pre_fl.id)
        self.assertEqual(ol.floorplan.floor, 3)
        self.assertIsInstance(ol.floorplan.image, ImageFieldFile)
        self.assertEqual(ol.indoor, '-110,110')

    def test_change_indoor_missing_indoor_position(self):
        self._login_as_admin()
        p = self._get_prefix()
        obj = self._create_object(name='test-change-indoor')
        pre_loc = self._create_location(type='indoor')
        pre_fl = self._create_floorplan(location=pre_loc)
        ol = self._create_object_location(
            content_object=obj, location=pre_loc, floorplan=pre_fl, indoor='-100,100'
        )
        # -- post changes
        params = self.params
        params.update(
            {
                'name': obj.name,
                '{0}-0-type'.format(p): 'indoor',
                '{0}-0-location_selection'.format(p): 'existing',
                '{0}-0-location'.format(p): pre_loc.id,
                '{0}-0-name'.format(p): pre_loc.name,
                '{0}-0-address'.format(p): pre_loc.address,
                '{0}-0-location-geometry'.format(p): pre_loc.geometry,
                '{0}-0-floorplan_selection'.format(p): 'existing',
                '{0}-0-floorplan'.format(p): pre_fl.id,
                '{0}-0-floor'.format(p): pre_fl.floor,
                '{0}-0-indoor'.format(p): '',
                '{0}-0-id'.format(p): ol.id,
                '{0}-INITIAL_FORMS'.format(p): '1',
            }
        )
        r = self.client.post(
            reverse(self.change_url, args=[obj.pk]), params, follow=True
        )
        self.assertContains(r, 'errors field-indoor')

    def test_add_outdoor_invalid(self):
        self._login_as_admin()
        p = self._get_prefix()
        params = self.params
        params.update(
            {
                'name': 'test-outdoor-invalid',
                '{0}-0-type'.format(p): 'outdoor',
                '{0}-0-location_selection'.format(p): 'new',
                '{0}-0-location'.format(p): '',
                '{0}-0-name'.format(p): '',
                '{0}-0-address'.format(p): '',
                '{0}-0-geometry'.format(p): '',
            }
        )
        r = self.client.post(reverse(self.add_url), params, follow=True)
        self.assertContains(r, 'errors field-name')
        self.assertContains(r, 'errors field-address')
        self.assertContains(r, 'errors field-geometry')

    def test_add_outdoor_invalid_geometry(self):
        self._login_as_admin()
        p = self._get_prefix()
        params = self.params
        params.update(
            {
                'name': 'test-outdoor-invalid-geometry',
                '{0}-0-type'.format(p): 'outdoor',
                '{0}-0-location_selection'.format(p): 'new',
                '{0}-0-location'.format(p): '',
                '{0}-0-geometry'.format(p): 'INVALID',
            }
        )
        r = self.client.post(reverse(self.add_url), params, follow=True)
        self.assertContains(r, 'errors field-geometry')

    def test_add_mobile(self):
        self._login_as_admin()
        p = self._get_prefix()
        params = self.params
        params.update(
            {
                'name': 'test-add-mobile',
                '{0}-0-type'.format(p): 'outdoor',
                '{0}-0-is_mobile'.format(p): True,
                '{0}-0-location_selection'.format(p): 'new',
                '{0}-0-name'.format(p): '',
                '{0}-0-address'.format(p): '',
                '{0}-0-geometry'.format(p): '',
            }
        )
        self.assertEqual(self.location_model.objects.count(), 0)
        r = self.client.post(reverse(self.add_url), params, follow=True)
        self.assertNotContains(r, 'errors')
        self.assertEqual(self.location_model.objects.filter(is_mobile=True).count(), 1)
        self.assertEqual(self.object_location_model.objects.count(), 1)
        loc = self.location_model.objects.first()
        self.assertEqual(
            loc.objectlocation_set.first().content_object.name, params['name']
        )
        self.assertEqual(loc.name, params['name'])

    def test_change_mobile(self):
        self._login_as_admin()
        obj = self._create_object(name='test-change-mobile')
        pre_loc = self._create_location(name=obj.name, is_mobile=True)
        ol = self._create_object_location(content_object=obj, location=pre_loc)
        p = self._get_prefix()
        params = self.params
        params.update(
            {
                'name': 'test-change-mobile',
                '{0}-0-type'.format(p): 'outdoor',
                '{0}-0-is_mobile'.format(p): True,
                '{0}-0-location'.format(p): pre_loc.id,
                '{0}-0-name'.format(p): '',
                '{0}-0-address'.format(p): '',
                '{0}-0-geometry'.format(p): '',
                '{0}-0-location_selection'.format(p): 'new',
                '{0}-0-id'.format(p): ol.id,
                '{0}-INITIAL_FORMS'.format(p): '1',
            }
        )
        self.assertEqual(self.location_model.objects.count(), 1)
        r = self.client.post(
            reverse(self.change_url, args=[obj.pk]), params, follow=True
        )
        self.assertNotContains(r, 'errors')
        self.assertEqual(self.object_location_model.objects.count(), 1)
        self.assertEqual(self.location_model.objects.filter(is_mobile=True).count(), 1)
        loc = self.location_model.objects.first()
        self.assertEqual(
            loc.objectlocation_set.first().content_object.name, params['name']
        )

    def test_change_indoor_missing_floorplan_pk(self):
        self._login_as_admin()
        p = self._get_prefix()
        obj = self._create_object(name='test-floorplan-error')
        pre_loc = self._create_location(type='indoor')
        pre_fl = self._create_floorplan(location=pre_loc)
        ol = self._create_object_location(
            content_object=obj, location=pre_loc, floorplan=pre_fl, indoor='-100,100'
        )
        # -- post changes
        params = self.params
        params.update(
            {
                'name': obj.name,
                '{0}-0-type'.format(p): 'indoor',
                '{0}-0-location_selection'.format(p): 'existing',
                '{0}-0-location'.format(p): pre_loc.id,
                '{0}-0-name'.format(p): pre_loc.name,
                '{0}-0-type'.format(p): pre_loc.type,
                '{0}-0-is_mobile'.format(p): pre_loc.is_mobile,
                '{0}-0-address'.format(p): pre_loc.address,
                '{0}-0-location-geometry'.format(p): pre_loc.geometry,
                '{0}-0-floorplan_selection'.format(p): 'existing',
                '{0}-0-floorplan'.format(p): '',
                '{0}-0-floor'.format(p): pre_fl.floor,
                '{0}-0-indoor'.format(p): '-100,100',
                '{0}-0-id'.format(p): ol.id,
                '{0}-INITIAL_FORMS'.format(p): '1',
            }
        )
        r = self.client.post(
            reverse(self.change_url, args=[obj.pk]), params, follow=True
        )
        self.assertContains(r, 'errors field-floorplan')
        self.assertContains(r, 'No floorplan selected')

    def test_change_indoor_floorplan_doesnotexist(self):
        self._login_as_admin()
        p = self._get_prefix()
        obj = self._create_object(name='test-floorplan-error')
        pre_loc = self._create_location(type='indoor')
        pre_fl = self._create_floorplan(location=pre_loc)
        ol = self._create_object_location(
            content_object=obj, location=pre_loc, floorplan=pre_fl, indoor='-100,100'
        )
        # -- post changes
        params = self.params
        params.update(
            {
                'name': obj.name,
                '{0}-0-type'.format(p): 'indoor',
                '{0}-0-location_selection'.format(p): 'existing',
                '{0}-0-location'.format(p): pre_loc.id,
                '{0}-0-name'.format(p): pre_loc.name,
                '{0}-0-type'.format(p): pre_loc.type,
                '{0}-0-is_mobile'.format(p): pre_loc.is_mobile,
                '{0}-0-address'.format(p): pre_loc.address,
                '{0}-0-location-geometry'.format(p): pre_loc.geometry,
                '{0}-0-floorplan_selection'.format(p): 'existing',
                '{0}-0-floorplan'.format(p): self.floorplan_model().id,
                '{0}-0-floor'.format(p): pre_fl.floor,
                '{0}-0-indoor'.format(p): '-100,100',
                '{0}-0-id'.format(p): ol.id,
                '{0}-INITIAL_FORMS'.format(p): '1',
            }
        )
        r = self.client.post(
            reverse(self.change_url, args=[obj.pk]), params, follow=True
        )
        self.assertContains(r, 'errors field-floorplan')
        self.assertContains(r, 'Selected floorplan does not exist')

    def test_change_indoor_floorplan_different_location(self):
        self._login_as_admin()
        p = self._get_prefix()
        obj = self._create_object(name='test-floorplan-error')
        pre_loc = self._create_location(type='indoor')
        pre_fl = self._create_floorplan(location=pre_loc)
        ol = self._create_object_location(
            content_object=obj, location=pre_loc, floorplan=pre_fl, indoor='-100,100'
        )
        fl = self._create_floorplan()
        # -- post changes
        params = self.params
        params.update(
            {
                'name': obj.name,
                '{0}-0-type'.format(p): 'indoor',
                '{0}-0-location_selection'.format(p): 'existing',
                '{0}-0-location'.format(p): pre_loc.id,
                '{0}-0-name'.format(p): pre_loc.name,
                '{0}-0-address'.format(p): pre_loc.address,
                '{0}-0-location-geometry'.format(p): pre_loc.geometry,
                '{0}-0-floorplan_selection'.format(p): 'existing',
                '{0}-0-floorplan'.format(p): fl.id,
                '{0}-0-floor'.format(p): pre_fl.floor,
                '{0}-0-indoor'.format(p): '-100,100',
                '{0}-0-id'.format(p): ol.id,
                '{0}-INITIAL_FORMS'.format(p): '1',
            }
        )
        r = self.client.post(
            reverse(self.change_url, args=[obj.pk]), params, follow=True
        )
        self.assertContains(r, 'errors field-floorplan')
        self.assertContains(r, 'This floorplan is associated to a different location')

    def test_missing_type_error(self):
        self._login_as_admin()
        p = self._get_prefix()
        params = self.params
        params.update(
            {
                'name': 'test-outdoor-add-new',
                '{0}-0-type'.format(p): '',
                '{0}-0-location_selection'.format(p): 'new',
                '{0}-0-location'.format(p): '',
                '{0}-0-floorplan_selection'.format(p): '',
                '{0}-0-floorplan'.format(p): '',
                '{0}-0-floor'.format(p): '',
                '{0}-0-image'.format(p): '',
                '{0}-0-indoor'.format(p): '',
                '{0}-0-id'.format(p): '',
            }
        )
        r = self.client.post(reverse(self.add_url), params, follow=True)
        self.assertContains(r, 'errors field-type')

    def test_add_indoor_location_without_indoor_coords(self):
        self._login_as_admin()
        p = self._get_prefix()
        params = self.params
        params.update(
            {
                'name': 'test-add-indoor-location-without-coords',
                '{0}-0-type'.format(p): 'indoor',
                '{0}-0-location_selection'.format(p): 'new',
                '{0}-0-location'.format(p): '',
                '{0}-0-floorplan_selection'.format(p): 'new',
                '{0}-0-floorplan'.format(p): '',
                '{0}-0-floor'.format(p): '',
                '{0}-0-image'.format(p): '',
                '{0}-0-indoor'.format(p): '',
                '{0}-0-id'.format(p): '',
            }
        )
        r = self.client.post(reverse(self.add_url), params, follow=True)
        self.assertNotContains(r, 'errors')
        loc = self.location_model.objects.get(name=params['{0}-0-name'.format(p)])
        self.assertEqual(loc.address, params['{0}-0-address'.format(p)])
        self.assertEqual(loc.objectlocation_set.count(), 1)
        self.assertEqual(self.location_model.objects.count(), 1)
        self.assertEqual(self.floorplan_model.objects.count(), 0)
        ol = loc.objectlocation_set.first()
        self.assertEqual(ol.content_object.name, params['name'])
        self.assertEqual(ol.location.type, 'indoor')
        self.assertEqual(ol.indoor, '')

    def test_add_indoor_location_without_coords(self):
        self._login_as_admin()
        p = self._get_prefix()
        floorplan_file = open(self._floorplan_path, 'rb')
        params = self.params
        params.update(
            {
                'name': 'test-add-indoor-location-without-coords',
                '{0}-0-type'.format(p): 'indoor',
                '{0}-0-location_selection'.format(p): 'new',
                '{0}-0-location'.format(p): '',
                '{0}-0-floorplan_selection'.format(p): 'new',
                '{0}-0-floorplan'.format(p): '',
                '{0}-0-floor'.format(p): '1',
                '{0}-0-image'.format(p): floorplan_file,
                '{0}-0-indoor'.format(p): '',
                '{0}-0-id'.format(p): '',
            }
        )
        r = self.client.post(reverse(self.add_url), params, follow=True)
        floorplan_file.close()
        self.assertContains(r, 'error')
        loc = self.location_model.objects.filter(name=params['{0}-0-name'.format(p)])
        self.assertEqual(loc.count(), 0)

    def test_add_indoor_location_without_floor(self):
        p = self._get_prefix()
        floorplan_file = open(self._floorplan_path, 'rb')
        params = self.params
        params.update(
            {
                'name': 'test-add-indoor-location-without-coords',
                '{0}-0-type'.format(p): 'indoor',
                '{0}-0-location_selection'.format(p): 'new',
                '{0}-0-location'.format(p): '',
                '{0}-0-floorplan_selection'.format(p): 'new',
                '{0}-0-floorplan'.format(p): '',
                '{0}-0-floor'.format(p): '',
                '{0}-0-image'.format(p): floorplan_file,
                '{0}-0-indoor'.format(p): '-100,100',
                '{0}-0-id'.format(p): '',
            }
        )
        r = self.client.post(reverse(self.add_url), params)
        floorplan_file.close()
        self.assertEqual(r.status_code, 302)
