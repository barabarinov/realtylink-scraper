import logging
from dataclasses import dataclass

from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app.utils import handle_exception

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


@dataclass
class Apartment:
    link: str
    title: str
    region: str
    address: str
    description: str
    datetime: str
    price: float
    rooms: int
    floor_area: float
    image_array: list[str]


class ApartmentsScraper:
    def __init__(self, base_url, max_apartments: int = 60) -> None:
        self.driver = webdriver.Chrome()
        self.base_url = base_url
        self.max_apartments = max_apartments

    def scrape(self) -> list[Apartment]:
        self.driver.maximize_window()
        self.driver.get(self.base_url)
        self._wait_for_element_download(By.CSS_SELECTOR, "a.property-thumbnail-summary-link", timeout=10)
        apartments_links = self._extract_apartment_links()

        return [self.scrape_apartment(apartment_link) for apartment_link in apartments_links]

    def _extract_apartment_links(self) -> list[str]:
        apartments_data = []

        while True:
            link_selector = "a.property-thumbnail-summary-link"
            self._wait_for_element_download(By.CSS_SELECTOR, link_selector, timeout=10)

            apartments = self.driver.find_elements(By.CSS_SELECTOR, link_selector)

            for apartment in apartments:
                apartments_data.append(apartment.get_attribute("href"))
                logging.info(apartment.get_attribute("href"))
                if len(apartments_data) == self.max_apartments:
                    return apartments_data
            try:
                next_button_li = self.driver.find_element(By.CSS_SELECTOR, "li.next")
                next_button_classes = next_button_li.get_attribute("class").split()
                if "inactive" in next_button_classes:
                    break
                next_button_li.find_element(By.TAG_NAME, "a").click()
                self.driver.refresh()
            except NoSuchElementException:
                break

        return apartments_data

    def scrape_apartment(self, apartment_link: str) -> Apartment:
        self.driver.get(apartment_link)
        self._wait_for_element_download(By.ID, "pre-localisation-section")

        return Apartment(
            link=apartment_link,
            title=self._get_title(),
            region=self._get_region(),
            address=self._get_region(address=True),
            description=self._get_description(),
            datetime="Today",
            price=self._get_price(),
            rooms=self._get_bedrooms_amount() + self._get_bathrooms_amount(),
            floor_area=self._get_floor_area(),
            image_array=self._get_photo_urls_array(),
        )

    def _get_element(self, by: str, selector: str) -> str:
        return self.driver.find_element(
            by, selector
        ).text.strip()

    def _get_title(self) -> str:
        return self._get_element(
            By.CSS_SELECTOR, "h1[itemprop='category'] > span[data-id='PageTitle']"
        )

    def _get_region(self, address: bool = False) -> str:
        data = self._get_element(By.CSS_SELECTOR, "h2[itemprop='address']")
        if address:
            return data
        return ", ".join(data.split(", ")[-2:])

    @handle_exception(default_value="No description")
    def _get_description(self) -> str:
        return self._get_element(By.CSS_SELECTOR, 'div[itemprop="description"]')

    @handle_exception(default_value=0)
    def _get_price(self) -> float:
        element_text = self._get_element(
            By.CSS_SELECTOR, "div.price.text-right > span:nth-child(6)"
        )
        try:
            return int(element_text.split(" ")[0].lstrip("$").replace(",", ""))
        except ValueError:
            logging.error(f"Cannot convert price to integer: {element_text}")

    @handle_exception(default_value=0)
    def _get_floor_area(self) -> int:
        element_text = self._get_element(
            By.CSS_SELECTOR, "div.carac-value > span"
        )
        if " " not in element_text:
            logging.error(f"Invalid floor area text format: {element_text}")
            raise ValueError(f"Invalid floor area text format: {element_text}")
        try:
            return int(element_text.split(" ")[0].replace(",", ""))
        except ValueError:
            logging.error(f"Cannot convert floor area to integer: {element_text}")

    @handle_exception(default_value=0)
    def _get_bedrooms_amount(self) -> int:
        element_text = self._get_element(By.CSS_SELECTOR, "div.row.teaser > div.cac")
        if " " not in element_text:
            logging.error(f"Invalid bedroom amount text format: {element_text}")
            raise ValueError(f"Invalid bedroom amount text format: {element_text}")
        try:
            return int(element_text.split(" ")[0])
        except ValueError:
            logging.error(f"Cannot convert bedrooms amount to integer: {element_text}")
            return 0

    @handle_exception(default_value=0)
    def _get_bathrooms_amount(self) -> int:
        element_text = self._get_element(By.CSS_SELECTOR, "div.row.teaser > div.sdb")
        if " " not in element_text:
            logging.error(f"Invalid bathroom amount text format: {element_text}")
            raise ValueError(f"Invalid bathroom amount text format: {element_text}")
        try:
            return int(element_text.split(" ")[0])
        except ValueError:
            logging.error(f"Cannot convert bathrooms amount to integer: {element_text}")
            return 0

    def _wait_for_element_download(
        self, by: str, selector: str, timeout: int = 3
    ) -> None:
        WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located((by, selector))
        )

    def _get_photo_urls_array(self) -> list[str] | None:
        try:
            self.driver.find_element(
                By.CSS_SELECTOR, "div.primary-photo-container > a"
            ).click()

            photo_count_selector = "div.description > strong"
            self._wait_for_element_download(By.CSS_SELECTOR, photo_count_selector)

            photo_count_text = self.driver.find_element(
                By.CSS_SELECTOR, photo_count_selector
            ).text

            if "/" not in photo_count_text or len(photo_count_text.split("/")) != 2:
                logging.error(f"Invalid photo count text format: {photo_count_text}")
                raise ValueError(f"Invalid photo count text format: {photo_count_text}")
            try:
                total_photo_count = int(photo_count_text.split("/")[1])
            except ValueError as e:
                logging.error(f"Cannot convert photo count to integer: {photo_count_text.split('/')[1]}")
                raise ValueError(f"Cannot convert photo count to integer: {photo_count_text.split('/')[1]}") from e

            photo_urls = []
            action_chain = ActionChains(self.driver)

            while len(photo_urls) < total_photo_count:
                current_photo_url = self.driver.find_element(
                    By.ID, "fullImg"
                ).get_attribute("src")
                photo_urls.append(current_photo_url)
                action_chain.send_keys(Keys.ARROW_RIGHT).perform()

            return photo_urls
        except TimeoutException:
            return None
