import pprint
import time

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app.utils import handle_no_such_element_exception

BASE_URL = "https://realtylink.org/en/properties~for-rent"
MAX_APARTMENTS = 60


class ApartmentsScraper:
    def __init__(self) -> None:
        self.driver = webdriver.Chrome()
        self.base_url = BASE_URL

    def _wait_for_element_and_click(
        self, by: str, selector: str, timeout: int = 3
    ) -> None:
        WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located((by, selector))
        )

    def _get_title(self) -> str:
        return self.driver.find_element(
            By.CSS_SELECTOR, "h1[itemprop='category'] > span[data-id='PageTitle']"
        ).text.strip()

    def _get_region(self, address: bool = False) -> str:
        data = self.driver.find_element(
            By.CSS_SELECTOR, "h2[itemprop='address']"
        ).text.strip()
        if address:
            return data
        return ", ".join(data.split(", ")[-2:])

    @handle_no_such_element_exception(value="No description")
    def _get_description(self) -> str:
        return self.driver.find_element(
            By.CSS_SELECTOR, 'div[itemprop="description"]'
        ).text.strip()

    def _get_price(self) -> str:
        return self.driver.find_element(
            By.CSS_SELECTOR,
            "div.price.text-right > span:nth-child(6)",
        ).text.strip()

    def _get_floor_area(self) -> str:
        return (
            self.driver.find_element(By.CSS_SELECTOR, "div.carac-value > span")
            .text.strip()
            .split(" ")[0]
        )

    @handle_no_such_element_exception(value=0)
    def _get_bedrooms_amount(self) -> int:
        return int(
            self.driver.find_element(By.CSS_SELECTOR, "div.row.teaser > div.cac")
            .text.strip()
            .split(" ")[0] or 0
        )

    @handle_no_such_element_exception(value=0)
    def _get_bathrooms_amount(self) -> int:
        return int(
            self.driver.find_element(By.CSS_SELECTOR, "div.row.teaser > div.sdb")
            .text.strip()
            .split(" ")[0] or 0
        )

    def _get_total_photo_count(self) -> int:
        photo_count_selector = "div.description > strong"
        self._wait_for_element_and_click(By.CSS_SELECTOR, photo_count_selector)

        photo_count_text = self.driver.find_element(
            By.CSS_SELECTOR, photo_count_selector
        ).text

        return int(photo_count_text.split("/")[1])

    def _collect_photo_urls(self, total_photo_count: int) -> list[str]:
        photo_urls = []
        action_chain = ActionChains(self.driver)

        while len(photo_urls) < total_photo_count:
            current_photo_url = self.driver.find_element(
                By.ID, "fullImg"
            ).get_attribute("src")
            photo_urls.append(current_photo_url)
            action_chain.send_keys(Keys.ARROW_RIGHT).perform()

        return photo_urls

    def _get_photo_urls_array(self) -> list[str] | None:
        try:
            # photo_selector = "button.btn.btn-primary.photo-btn"
            # self._wait_for_element_and_click(By.CSS_SELECTOR, photo_selector, timeout=4)
            #
            # button = self.driver.find_element(
            #     By.CSS_SELECTOR,
            #     photo_selector,
            # )
            # self.driver.execute_script("arguments[0].click();", button)
            self.driver.find_element(
                By.CSS_SELECTOR, "div.primary-photo-container > a"
            ).click()
            time.sleep(1)

            total_photo_count = self._get_total_photo_count()

            return self._collect_photo_urls(total_photo_count)
        except TimeoutException:
            return None

    def _extract_apartment_links(self, n: int = MAX_APARTMENTS) -> list[str]:
        apartments_data = []

        while True:
            link_selector = "a.property-thumbnail-summary-link"
            self._wait_for_element_and_click(By.CSS_SELECTOR, link_selector)

            apartments = self.driver.find_elements(By.CSS_SELECTOR, link_selector)
            for apartment in apartments:
                apartments_data.append(apartment.get_attribute("href"))
                if len(apartments_data) == n:
                    return apartments_data

            self.driver.find_element(By.CSS_SELECTOR, "li.next > a").click()

    def scrape_apartment(self, apartment_link: str) -> dict:
        self.driver.get(apartment_link)
        self._wait_for_element_and_click(By.ID, "pre-localisation-section")

        return {
            "link": apartment_link,
            "title": self._get_title(),
            "region": self._get_region(),
            "address": self._get_region(address=True),
            "description": self._get_description(),
            "datetime": "Today",
            "price": self._get_price(),
            "rooms": self._get_bedrooms_amount() + self._get_bathrooms_amount(),
            "floor_area": self._get_floor_area(),
            "image_array": self._get_photo_urls_array(),
        }

    def scrape(self) -> list[dict[str, str]]:
        self.driver.maximize_window()
        self.driver.get(self.base_url)
        time.sleep(5)

        apartments_links = self._extract_apartment_links()

        apartments_list = []

        for apartment_link in apartments_links:
            apartments_list.append(self.scrape_apartment(apartment_link))
            pprint.pprint(apartments_list)

        print("✅ Scraped successfully")
        return apartments_list
