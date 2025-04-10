from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from ..models import Location, ObjectLocation
from .base.test_selenium import BaseTestDeviceAdminSelenium
from .testdeviceapp.models import Device


class TestDeviceAdminSelenium(BaseTestDeviceAdminSelenium, StaticLiveServerTestCase):
    user_model = get_user_model()
    object_model = Device
    location_model = Location
    object_location_model = ObjectLocation
