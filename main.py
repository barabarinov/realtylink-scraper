import argparse
import json
import logging

from app.apartments_scraper import ApartmentsScraper

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scrape apartment data and save to a JSON file."
    )
    parser.add_argument(
        "--output",
        nargs="?",
        type=str,
        default="apartments.json",
    )
    args = parser.parse_args()

    scraper = ApartmentsScraper()
    apartments_list = scraper.scrape()
    logging.info("✅ Scraped successfully")

    with open(args.output, 'w', encoding='utf-8') as file:
        json.dump(apartments_list, file, ensure_ascii=False, indent=4)
