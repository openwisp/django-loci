from channels.testing import ChannelsLiveServerTestCase
from django.contrib.auth import get_user_model
from django.test import tag
from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from django_loci.models import Location, ObjectLocation
from django_loci.tests import TestAdminMixin, TestLociMixin
from openwisp_utils.tests.selenium import SeleniumTestMixin


@tag("selenium_tests")
class TestCommonLocationWebsocket(
    SeleniumTestMixin, TestLociMixin, TestAdminMixin, ChannelsLiveServerTestCase
):
    location_model = Location
    object_location_model = ObjectLocation
    user_model = get_user_model()

    def _wait_for_websocket_update(self, condition):
        return self.wait_until(condition, timeout=5)

    def test_common_location_broadcast_ws(self):
        self.login()
        location1 = self._create_location(is_mobile=True, name="Location 1")
        location2 = self._create_location(is_mobile=True, name="Location 2")
        self.open(reverse("admin:location-broadcast-listener"))
        self._wait_for_websocket_update(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "#ws-connected"),
            ),
        )
        # Update location to trigger websocket message
        location1.geometry = (
            '{ "type": "Point", "coordinates": [ 77.218791, 28.6324252 ] }'
        )
        location1.address = "Delhi, India"
        location1.full_clean()
        location1.save()
        # Wait for websocket message to be received
        self._wait_for_websocket_update(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#location-updates li"),
                "77.218791",
            ),
        )
        location2.geometry = (
            '{ "type": "Point", "coordinates": [72.877656, 19.075984] }'
        )
        location2.address = "Mumbai, India"
        location2.full_clean()
        location2.save()
        self._wait_for_websocket_update(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#location-updates"),
                "72.877656",
            ),
        )
