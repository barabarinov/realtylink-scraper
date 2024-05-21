from dataclasses import dataclass

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app.utils import handle_exception


@dataclass
class Apartment:
    link: str
    title: str
    region: str
    address: str
    description: str
    datetime: str
    price: str
    rooms: int
    floor_area: str
    image_array: list[str]


class ApartmentsScraper:
    def __init__(self, base_url, max_apartments: int = 60) -> None:
        self.driver = webdriver.Chrome()
        self.base_url = base_url
        self.max_apartments = max_apartments

    def scrape(self) -> list[Apartment]:
        self.driver.maximize_window()
        self.driver.get(self.base_url)
        self._wait_for_element_download(By.CSS_SELECTOR, "div.wrapper.even.wrapper-results")

        apartments_links = self._extract_apartment_links()

        return [self.scrape_apartment(apartment_link) for apartment_link in apartments_links]

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

    @handle_exception(default_value="No description")
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

    @handle_exception(default_value=0)
    def _get_bedrooms_amount(self) -> int:
        return int(
            self.driver.find_element(By.CSS_SELECTOR, "div.row.teaser > div.cac")
            .text.strip()
            .split(" ")[0] or 0
        )

    @handle_exception(default_value=0)
    def _get_bathrooms_amount(self) -> int:
        return int(
            self.driver.find_element(By.CSS_SELECTOR, "div.row.teaser > div.sdb")
            .text.strip()
            .split(" ")[0] or 0
        )

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

            total_photo_count = int(photo_count_text.split("/")[1])  # TODO

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

    def _extract_apartment_links(self) -> list[str]:
        apartments_data = []

        while True:
            link_selector = "a.property-thumbnail-summary-link"
            self._wait_for_element_download(By.CSS_SELECTOR, link_selector)

            apartments = self.driver.find_elements(By.CSS_SELECTOR, link_selector)
            for apartment in apartments:
                apartments_data.append(apartment.get_attribute("href"))
                if len(apartments_data) == self.max_apartments:
                    return apartments_data

            self.driver.find_element(By.CSS_SELECTOR, "li.next > a").click()
