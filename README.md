# realtylink-scraper

This scraper gathers information about rental apartments from the website https://realtylink.org/en/properties~for-rent.

It collects the following details for each apartment:

+ Link: The URL of the apartment listing
+ Title: The name or title of the apartment
+ Region: The general area or neighborhood where the apartment is located
+ Address: The specific street address of the apartment
+ Description: A detailed description of the apartment, including features and amenities
+ Datetime: The date and time the listing was posted
+ Price: The monthly rent for the apartment
+ Rooms: The number of bedrooms and bathrooms in the apartment
+ Floor area: The size of the apartment in square meters
+ Image array: A list of URLs for the apartment's photos

Once the scraper has gathered all of this information, it saves it to a JSON file.

### Quickstart:
```shell
git clone https://github.com/barabarinov/realtylink-scraper.git
python -m venv venv
pip install -r requirements.txt
```

### To run script use the following command:
```shell
python main.py
```
