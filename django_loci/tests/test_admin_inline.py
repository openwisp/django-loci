import glob
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import GEOSGeometry
from django.db.models.fields.files import ImageFieldFile
from django.test import TestCase
from django.urls import reverse

from . import TestAdminMixin, TestLociMixin
from ..models import FloorPlan, Location, ObjectLocation
from .testdeviceapp.models import Device


class TestAdminInline(TestAdminMixin, TestLociMixin, TestCase):
    object_model = Device
    location_model = Location
    floorplan_model = FloorPlan
    object_location_model = ObjectLocation
    user_model = get_user_model()
    app_label = 'django_loci'
    inline_field_prefix = 'objectlocation-content_type-object_id'
    _p = '{0}-{1}'.format(app_label, inline_field_prefix)
    _params = {
        '{0}-0-name'.format(_p): 'Centro Piazza Venezia',
        '{0}-0-address'.format(_p): 'Piazza Venezia, Roma, Italia',
        '{0}-0-geometry'.format(_p): '{"type": "Point", "coordinates": [12.512124, 41.898903]}',
        '{0}-TOTAL_FORMS'.format(_p): '1',
        '{0}-INITIAL_FORMS'.format(_p): '0',
        '{0}-MIN_NUM_FORMS'.format(_p): '0',
        '{0}-MAX_NUM_FORMS'.format(_p): '1',
    }

    @classmethod
    def tearDownClass(cls):
        for fl in glob.glob(os.path.join(settings.BASE_DIR, 'media/floorplan_*')):
            os.remove(fl)

    def test_json_urls(self):
        self._login_as_admin()
        r = self.client.get(reverse('admin:testdeviceapp_device_add'))
        url = reverse('admin:django_loci_location_json', args=['0000'])
        self.assertContains(r, url)
        url = reverse('admin:django_loci_location_floorplans_json', args=['0000'])
        self.assertContains(r, url)

    def test_add_outdoor_new(self):
        self._login_as_admin()
        p = self._p
        params = self._params.copy()
        params.update({
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
        })
        r = self.client.post(reverse('admin:testdeviceapp_device_add'), params, follow=True)
        self.assertNotContains(r, 'errors')
        loc = self.location_model.objects.get(name=params['{0}-0-name'.format(p)])
        self.assertEqual(loc.address, params['{0}-0-address'.format(p)])
        self.assertEqual(loc.geometry.coords, GEOSGeometry(params['{0}-0-geometry'.format(p)]).coords)
        self.assertEqual(loc.objectlocation_set.count(), 1)
        self.assertEqual(loc.objectlocation_set.first().content_object.name, params['name'])

    def test_add_outdoor_existing(self):
        self._login_as_admin()
        p = self._p
        pre_loc = self._create_location()
        params = self._params.copy()
        params.update({
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
        })
        r = self.client.post(reverse('admin:testdeviceapp_device_add'), params, follow=True)
        self.assertNotContains(r, 'errors')
        loc = self.location_model.objects.get(name=params['{0}-0-name'.format(p)])
        self.assertEqual(pre_loc.id, loc.id)
        self.assertEqual(loc.address, params['{0}-0-address'.format(p)])
        self.assertEqual(loc.geometry.coords, GEOSGeometry(params['{0}-0-geometry'.format(p)]).coords)
        self.assertEqual(loc.objectlocation_set.count(), 1)
        self.assertEqual(loc.objectlocation_set.first().content_object.name, params['name'])
        self.assertEqual(self.location_model.objects.count(), 1)

    def test_change_outdoor(self):
        self._login_as_admin()
        p = self._p
        obj = self._create_object(name='test-change-outdoor')
        pre_loc = self._create_location()
        ol = self._create_object_location(type='outdoor',
                                          location=pre_loc,
                                          content_object=obj)
        # -- ensure change form doesn't raise any exception
        r = self.client.get(reverse('admin:testdeviceapp_device_change', args=[obj.pk]))
        self.assertContains(r, obj.name)
        # -- post changes
        params = self._params.copy()
        params.update({
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
        })
        r = self.client.post(reverse('admin:testdeviceapp_device_change', args=[obj.pk]), params, follow=True)
        self.assertNotContains(r, 'errors')
        loc = self.location_model.objects.get(name=params['{0}-0-name'.format(p)])
        self.assertEqual(pre_loc.id, loc.id)
        self.assertEqual(loc.address, params['{0}-0-address'.format(p)])
        self.assertEqual(loc.geometry.coords, GEOSGeometry(params['{0}-0-geometry'.format(p)]).coords)
        self.assertEqual(loc.objectlocation_set.count(), 1)
        self.assertEqual(loc.objectlocation_set.first().content_object.name, params['name'])
        self.assertEqual(self.location_model.objects.count(), 1)

    def test_change_outdoor_to_different_location(self):
        self._login_as_admin()
        p = self._p
        ol = self._create_object_location(type='outdoor')
        new_loc = self._create_location(name='different-location',
                                        address='Piazza Venezia, Roma, Italia',
                                        geometry='SRID=4326;POINT (12.512324 41.898703)')
        # -- post changes
        params = self._params.copy()
        changed_name = '{0} changed'.format(new_loc.name)
        params.update({
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
        })
        r = self.client.post(reverse('admin:testdeviceapp_device_change',
                                     args=[ol.content_object.pk]),
                             params, follow=True)
        self.assertNotContains(r, 'errors')
        loc = self.location_model.objects.get(name=changed_name)
        self.assertEqual(new_loc.id, loc.id)
        self.assertEqual(loc.address, params['{0}-0-address'.format(p)])
        self.assertEqual(loc.geometry.coords, GEOSGeometry(params['{0}-0-geometry'.format(p)]).coords)
        self.assertEqual(loc.objectlocation_set.count(), 1)
        self.assertEqual(loc.objectlocation_set.first().content_object.name, params['name'])
        self.assertEqual(self.location_model.objects.count(), 2)

    def test_add_indoor_new_location_new_floorplan(self):
        self._login_as_admin()
        p = self._p
        params = self._params.copy()
        floorplan_file = open(os.path.join(settings.BASE_DIR, 'media/floorplan.jpg'), 'rb')
        params.update({
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
        })
        r = self.client.post(reverse('admin:testdeviceapp_device_add'), params, follow=True)
        floorplan_file.close()
        self.assertNotContains(r, 'errors')
        loc = self.location_model.objects.get(name=params['{0}-0-name'.format(p)])
        self.assertEqual(loc.address, params['{0}-0-address'.format(p)])
        self.assertEqual(loc.geometry.coords, GEOSGeometry(params['{0}-0-geometry'.format(p)]).coords)
        self.assertEqual(loc.objectlocation_set.count(), 1)
        self.assertEqual(self.location_model.objects.count(), 1)
        self.assertEqual(self.floorplan_model.objects.count(), 1)
        ol = loc.objectlocation_set.first()
        self.assertEqual(ol.content_object.name, params['name'])
        self.assertEqual(ol.type, 'indoor')
        self.assertEqual(ol.floorplan.floor, 1)
        self.assertIsInstance(ol.floorplan.image, ImageFieldFile)
        self.assertEqual(ol.indoor, '-100,100')

    def test_add_indoor_existing_location_new_floorplan(self):
        self._login_as_admin()
        obj = self._create_object(name='test-add-indoor-existing-location-new-floorplan')
        pre_loc = self._create_location()
        p = self._p
        params = self._params.copy()
        floorplan_file = open(os.path.join(settings.BASE_DIR, 'media/floorplan.jpg'), 'rb')
        params.update({
            'name': obj.name,
            '{0}-0-type'.format(p): 'indoor',
            '{0}-0-location_selection'.format(p): 'existing',
            '{0}-0-location'.format(p): pre_loc.id,
            '{0}-0-name'.format(p): pre_loc.name,
            '{0}-0-address'.format(p): pre_loc.address,
            '{0}-0-geometry'.format(p): pre_loc.geometry.geojson,
            '{0}-0-floorplan_selection'.format(p): 'new',
            '{0}-0-floorplan'.format(p): '',
            '{0}-0-floor'.format(p): '1',
            '{0}-0-image'.format(p): floorplan_file,
            '{0}-0-indoor'.format(p): '-100,100',
            '{0}-0-id'.format(p): '',
        })
        r = self.client.post(reverse('admin:testdeviceapp_device_add'), params, follow=True)
        floorplan_file.close()
        self.assertNotContains(r, 'errors')
        loc = self.location_model.objects.get(name=params['{0}-0-name'.format(p)])
        self.assertEqual(loc.address, params['{0}-0-address'.format(p)])
        self.assertEqual(loc.geometry.coords, GEOSGeometry(params['{0}-0-geometry'.format(p)]).coords)
        self.assertEqual(loc.objectlocation_set.count(), 1)
        self.assertEqual(self.location_model.objects.count(), 1)
        self.assertEqual(self.floorplan_model.objects.count(), 1)
        ol = loc.objectlocation_set.first()
        self.assertEqual(ol.content_object.name, params['name'])
        self.assertEqual(ol.type, 'indoor')
        self.assertEqual(ol.floorplan.floor, 1)
        self.assertIsInstance(ol.floorplan.image, ImageFieldFile)
        self.assertEqual(ol.indoor, '-100,100')

    def test_add_indoor_existing_location_existing_floorplan(self):
        self._login_as_admin()
        obj = self._create_object(name='test-add-indoor-existing-location-new-floorplan')
        pre_loc = self._create_location()
        pre_fl = self._create_floorplan(location=pre_loc, floor=2)
        p = self._p
        params = self._params.copy()
        floorplan_file = open(os.path.join(settings.BASE_DIR, 'media/floorplan.jpg'), 'rb')
        changed_name = '{0} changed'.format(pre_loc.name)
        params.update({
            'name': obj.name,
            '{0}-0-type'.format(p): 'indoor',
            '{0}-0-location_selection'.format(p): 'existing',
            '{0}-0-location'.format(p): pre_loc.id,
            '{0}-0-name'.format(p): changed_name,
            '{0}-0-address'.format(p): pre_loc.address,
            '{0}-0-location-geometry'.format(p): pre_loc.geometry,
            '{0}-0-floorplan_selection'.format(p): 'existing',
            '{0}-0-floorplan'.format(p): pre_fl.id,
            '{0}-0-floor'.format(p): 3,  # floor
            '{0}-0-image'.format(p): '',
            '{0}-0-indoor'.format(p): '-110,110',
            '{0}-0-id'.format(p): '',
        })
        r = self.client.post(reverse('admin:testdeviceapp_device_add'), params, follow=True)
        floorplan_file.close()
        self.assertNotContains(r, 'errors')
        loc = self.location_model.objects.get(name=changed_name)
        self.assertEqual(loc.id, pre_loc.id)
        self.assertEqual(loc.address, params['{0}-0-address'.format(p)])
        self.assertEqual(loc.geometry.coords, GEOSGeometry(params['{0}-0-geometry'.format(p)]).coords)
        self.assertEqual(loc.objectlocation_set.count(), 1)
        self.assertEqual(self.location_model.objects.count(), 1)
        self.assertEqual(self.floorplan_model.objects.count(), 1)
        ol = loc.objectlocation_set.first()
        self.assertEqual(ol.content_object.name, params['name'])
        self.assertEqual(ol.type, 'indoor')
        self.assertEqual(ol.floorplan.id, pre_fl.id)
        self.assertEqual(ol.floorplan.floor, 3)
        self.assertIsInstance(ol.floorplan.image, ImageFieldFile)
        self.assertEqual(ol.indoor, '-110,110')
