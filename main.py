import argparse
import json
import logging
from dataclasses import asdict

from app.apartments_scraper import ApartmentsScraper

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

BASE_URL = "https://realtylink.org/en/properties~for-rent"


def main(args: argparse.Namespace) -> None:
    scraper = ApartmentsScraper(BASE_URL)
    apartments_list = scraper.scrape()
    logging.info("✅ Scraped successfully")

    with open(f"{args.output}.json", 'w', encoding='utf-8') as file:
        json.dump(
            [asdict(apartment) for apartment in apartments_list], file, ensure_ascii=False, indent=4
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scrape apartment data and save to a JSON file."
    )
    parser.add_argument(
        "--output",
        nargs="?",
        type=str,
        default="apartments",
    )
    main(parser.parse_args())
