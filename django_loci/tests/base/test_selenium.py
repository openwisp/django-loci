from django.urls.base import reverse
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait

from openwisp_utils.tests import SeleniumTestMixin

from .. import TestAdminInlineMixin, TestLociMixin


class BaseTestDeviceAdminSelenium(
    SeleniumTestMixin, TestAdminInlineMixin, TestLociMixin
):
    def _fill_device_form(self):
        """
        This method can be extended by downstram implementations
        needing more complex logic to fill the device form
        """
        self.find_element(by=By.NAME, value='name').send_keys('11:22:33:44:55:66')

    def test_create_new_device(self):
        self.login()
        self.open(reverse(self.add_url))
        self._fill_device_form()
        select = Select(
            self.find_element(
                by=By.NAME, value=f'{self._get_prefix()}-0-location_selection'
            )
        )
        select.select_by_value('new')

        select = Select(
            self.find_element(by=By.NAME, value=f'{self._get_prefix()}-0-type')
        )
        select.select_by_value('outdoor')

        self.find_element(by=By.NAME, value=f'{self._get_prefix()}-0-name').send_keys(
            'Test Location'
        )
        # use the marker button to select location on map
        self.find_element(
            by=By.XPATH, value='//a[@class="leaflet-draw-draw-marker"]'
        ).click()
        action = ActionChains(self.web_driver)
        # place the marker on the map at a random location
        elem = self.find_element(
            by=By.ID, value=f'id_{self._get_prefix()}-0-geometry-map'
        )
        # (15, 5) is a random offset from the top left corner of the map
        action.move_to_element(elem).move_by_offset(15, 5).click().perform()
        # Wait until address field gets populated with the location marked above
        WebDriverWait(self.web_driver, 5).until(
            lambda x: x.find_element(
                by=By.XPATH, value=f'//input[@name="{self._get_prefix()}-0-address"]'
            )
            .get_attribute('value')
            .strip()
            not in ('', None)
        )

        self.find_element(by=By.NAME, value='_save').click()
        self.wait_for_presence(By.CSS_SELECTOR, '.messagelist .success')
        # device model verbose name is dynamic
        object_verbose_name = self.object_model._meta.verbose_name
        self.assertEqual(
            self.find_elements(by=By.CLASS_NAME, value='success')[0].text,
            f'The {object_verbose_name} “11:22:33:44:55:66” was added successfully.',
        )
