from app.apartments_scraper import ApartmentsScraper
from app.writer import JSONWriter


if __name__ == '__main__':
    scraper = ApartmentsScraper()
    apartments_list = scraper.scrape()
    print("✅ Scraped successfully")

    json_writer = JSONWriter("apartments.json")
    json_writer.write(apartments_list)
