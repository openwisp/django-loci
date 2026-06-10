from time import sleep

from django.urls.base import reverse
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from openwisp_utils.tests import SeleniumTestMixin

from .. import TestAdminInlineMixin, TestLociMixin


class BaseTestDeviceAdminSelenium(
    SeleniumTestMixin, TestAdminInlineMixin, TestLociMixin
):
    app_label = "django_loci"

    def _fill_device_form(self):
        """
        This method can be extended by downstream implementations
        needing more complex logic to fill the device form
        """
        self.find_element(by=By.NAME, value="name").send_keys("11:22:33:44:55:66")

    def _mark_location_on_map(self, prefix):
        map_selector = f"#id_{prefix}-0-geometry-map"
        self.find_element(
            by=By.CSS_SELECTOR,
            value=f"{map_selector} .leaflet-draw-draw-marker",
        ).click()
        action = ActionChains(self.web_driver)
        elem = self.find_element(by=By.CSS_SELECTOR, value=map_selector)
        # Click slightly inside the map to avoid Leaflet controls on the edge.
        action.move_to_element(elem).move_by_offset(15, 5).click().perform()
        WebDriverWait(self.web_driver, 5).until(
            lambda x: x.find_element(
                by=By.XPATH, value=f'//input[@name="{prefix}-0-address"]'
            )
            .get_attribute("value")
            .strip()
            not in ("", None)
        )

    def _assert_device_added(self):
        self.find_element(by=By.NAME, value="_save").click()
        self.wait_for_presence(By.CSS_SELECTOR, ".messagelist .success")
        object_verbose_name = self.object_model._meta.verbose_name
        self.assertEqual(
            self.find_elements(by=By.CLASS_NAME, value="success")[0].text,
            f"The {object_verbose_name} “11:22:33:44:55:66” was added successfully.",
        )

    def _fill_location_fields(self, prefix):
        self.find_element(by=By.NAME, value=f"{prefix}-0-name").send_keys(
            "Test Location"
        )
        self.find_element(by=By.NAME, value=f"{prefix}-0-address").send_keys(
            "Piazza Venezia, Roma, Italia"
        )
        self.web_driver.execute_script(
            """
            arguments[0].value = JSON.stringify({
                type: "Point",
                coordinates: [12.512124, 41.898903]
            });
            arguments[0].dispatchEvent(new Event("change", { bubbles: true }));
            """,
            self.find_element(by=By.NAME, value=f"{prefix}-0-geometry"),
        )

    def test_create_new_device(self):
        self.login()
        self.open(reverse(self.add_url))
        self._fill_device_form()
        prefix = self._get_prefix()
        select = Select(
            self.find_element(by=By.NAME, value=f"{prefix}-0-location_selection")
        )
        select.select_by_value("new")

        select = Select(self.find_element(by=By.NAME, value=f"{prefix}-0-type"))
        select.select_by_value("outdoor")

        self.find_element(by=By.NAME, value=f"{prefix}-0-name").send_keys(
            "Test Location"
        )
        self._mark_location_on_map(prefix)
        self._assert_device_added()

    def test_recreate_location_inline_after_removal(self):
        self.login()
        self.open(reverse(self.add_url))
        self._fill_device_form()
        prefix = self._get_prefix()

        self.wait_for(
            "element_to_be_clickable",
            by=By.CSS_SELECTOR,
            value=".inline-group .inline-deletelink",
        ).click()
        self.wait_for(
            "element_to_be_clickable",
            by=By.CSS_SELECTOR,
            value=".inline-group .add-row a",
        ).click()

        select = Select(
            self.find_element(by=By.NAME, value=f"{prefix}-0-location_selection")
        )
        select.select_by_value("existing")
        WebDriverWait(self.web_driver, 5).until(
            lambda driver: driver.find_element(
                by=By.CSS_SELECTOR,
                value=".inline-group .inline-related:not(.empty-form) .field-location",
            ).is_displayed()
        )

        select = Select(
            self.find_element(by=By.NAME, value=f"{prefix}-0-location_selection")
        )
        select.select_by_value("new")
        WebDriverWait(self.web_driver, 5).until(
            lambda driver: driver.find_element(
                by=By.NAME, value=f"{prefix}-0-type"
            ).is_displayed()
        )

        Select(self.find_element(by=By.NAME, value=f"{prefix}-0-type")).select_by_value(
            "outdoor"
        )
        WebDriverWait(self.web_driver, 5).until(
            lambda driver: driver.find_element(
                by=By.NAME, value=f"{prefix}-0-name"
            ).is_displayed()
        )

        map_name = f"leafletmapid_{prefix}-0-geometry-map"
        initial_zoom = self.web_driver.execute_script(
            "return window[arguments[0]].getZoom();", map_name
        )
        self.find_element(
            by=By.CSS_SELECTOR,
            value=f"#id_{prefix}-0-geometry-map .leaflet-control-zoom-in",
        ).click()
        # Read Leaflet state directly to avoid waiting on tile/scale rendering in CI.
        WebDriverWait(self.web_driver, 5).until(
            lambda driver: driver.execute_script(
                "return window[arguments[0]].getZoom();", map_name
            )
            > initial_zoom
        )
        # Normal marker/geocoding behavior is covered by test_create_new_device.
        self._fill_location_fields(prefix)
        self._assert_device_added()

    def test_real_time_update_address_field(self):
        location = self._create_location()
        self.login()
        url = reverse(f"admin:{self.app_label}_location_change", args=[location.id])
        self.open(url)
        # Changing the address in tab 1 should update it in tab 0 in real time without a page reload
        self.web_driver.switch_to.new_window("tab")
        tabs = self.web_driver.window_handles
        # Swtich to last tab
        self.web_driver.switch_to.window(tabs[-1])
        self.open(url)
        address_input = self.find_element(by=By.ID, value="id_address")
        self.assertEqual(address_input.get_attribute("value"), location.address)
        self.find_element(
            by=By.XPATH, value='//a[@class="leaflet-draw-draw-marker"]'
        ).click()
        elem = self.find_element(by=By.ID, value="id_geometry-map")
        # Updating the marker to a random new location
        ActionChains(self.web_driver).move_to_element(elem).move_by_offset(
            30, 15
        ).click().perform()
        alert = WebDriverWait(self.web_driver, 2).until(EC.alert_is_present())
        alert.accept()
        sleep(0.05)
        new_address = "Lazio 00185, ITA"
        address_input = self.find_element(by=By.ID, value="id_address")
        self.assertIn(new_address, address_input.get_attribute("value"))
        self.wait_for("element_to_be_clickable", by=By.NAME, value="_continue").click()
        # Close tab[1] so other tests are not affected
        self.web_driver.close()
        # on some systems the zero tab may be an empty tab
        # hence we open the tab before the last one
        initial_tab = tabs.index(tabs[-1]) - 1
        self.web_driver.switch_to.window(tabs[initial_tab])
        address_input = self.find_element(by=By.ID, value="id_address")
        self.assertIn(new_address, address_input.get_attribute("value"))
