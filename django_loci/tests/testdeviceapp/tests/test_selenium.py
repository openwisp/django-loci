from channels.testing import ChannelsLiveServerTestCase
from django.contrib.auth import get_user_model
from django.test import tag
from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

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

    def test_common_location_broadcast_ws(self):
        self.login()
        mobile_location = self._create_location(is_mobile=True)
        self.open(reverse("admin:location-broadcast-listener"))
        WebDriverWait(self.web_driver, 3).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "#ws-connected"),
            )
        )
        # Update location to trigger websocket message
        mobile_location.geometry = (
            '{ "type": "Point", "coordinates": [ 77.218791, 28.6324252 ] }'
        )
        mobile_location.address = "Delhi, India"
        mobile_location.full_clean()
        mobile_location.save()
        # Wait for websocket message to be received
        WebDriverWait(self.web_driver, 3).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#location-updates li"),
                "77.218791",
            )
        )
