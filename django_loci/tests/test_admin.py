import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from . import TestAdminMixin, TestLociMixin
from ..models import FloorPlan, Location, ObjectLocation
from .testdeviceapp.models import Device


class TestAdmin(TestAdminMixin, TestLociMixin, TestCase):
    object_model = Device
    location_model = Location
    floorplan_model = FloorPlan
    object_location_model = ObjectLocation
    user_model = get_user_model()

    def test_location_list(self):
        self._login_as_admin()
        self._create_location(name='test-admin-location-1')
        r = self.client.get(reverse('admin:django_loci_location_changelist'))
        self.assertContains(r, 'test-admin-location-1')

    def test_floorplan_list(self):
        self._login_as_admin()
        self._create_floorplan()
        self._create_location()
        r = self.client.get(reverse('admin:django_loci_floorplan_changelist'))
        self.assertContains(r, '1st floor')

    def test_location_json_view(self):
        self._login_as_admin()
        loc = self._create_location()
        r = self.client.get(reverse('admin:django_loci_location_json', args=[loc.pk]))
        expected = {'name': loc.name,
                    'address': loc.address,
                    'type': loc.type,
                    'is_mobile': loc.is_mobile,
                    'geometry': json.loads(loc.geometry.json)}
        self.assertDictEqual(r.json(), expected)

    def test_location_floorplan_json_view(self):
        self._login_as_admin()
        fl = self._create_floorplan()
        r = self.client.get(reverse('admin:django_loci_location_floorplans_json', args=[fl.location.pk]))
        expected = {'choices': [
            {'id': str(fl.pk),
             'str': str(fl),
             'floor': fl.floor,
             'image': fl.image.url,
             'image_width': fl.image.width,
             'image_height': fl.image.height}
        ]}
        self.assertDictEqual(r.json(), expected)
