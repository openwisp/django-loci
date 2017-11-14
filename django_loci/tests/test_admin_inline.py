from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from . import TestAdminMixin, TestLociMixin
from ..models import FloorPlan, Location, ObjectLocation


class TestAdminInline(TestAdminMixin, TestLociMixin, TestCase):
    object_model = get_user_model()
    location_model = Location
    floorplan_model = FloorPlan
    object_location_model = ObjectLocation
    user_model = get_user_model()

    def test_json_urls(self):
        self._login_as_admin()
        r = self.client.get(reverse('admin:testdeviceapp_device_add'))
        url = reverse('admin:django_loci_location_json', args=['0000'])
        self.assertContains(r, url)
        url = reverse('admin:django_loci_location_floorplans_json', args=['0000'])
        self.assertContains(r, url)
