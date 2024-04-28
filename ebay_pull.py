import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
# -------------------------
# PULL FROM API
# -------------------------
class EbayAPI:

    def __init__(self, app_id, keyword, total_entries=1000):
        self.app_id = app_id
        self.keyword = keyword
        self.total_entries = total_entries

    def find_active_items(self):
        url = 'https://svcs.ebay.com/services/search/FindingService/v1'
        entries_per_page = 100
        items = []

        for page_number in range(1, (self.total_entries // entries_per_page) + 2):
            params = {
                'OPERATION-NAME': 'findItemsByKeywords',
                'SERVICE-VERSION': '1.13.0',
                'SECURITY-APPNAME': self.app_id,
                'GLOBAL-ID': 'EBAY-US',
                'RESPONSE-DATA-FORMAT': 'JSON',
                'keywords': self.keyword,
                'paginationInput.entriesPerPage': entries_per_page,
                'paginationInput.pageNumber': page_number,
                'sortOrder': 'EndTimeSoonest',
            }

            response = requests.get(url, params=params)
            if response.status_code == 200:
                json_response = response.json()
                search_result = json_response.get('findItemsByKeywordsResponse', [])[
                    0].get('searchResult', [{}])[0]
                items_on_page = search_result.get('item', [])
                items.extend(items_on_page)
                # Break if we have collected all items or if there are no more items to collect
                if len(items_on_page) < entries_per_page or len(items) >= self.total_entries:
                    break
            else:
                print(f"Error on page {page_number}: {response.status_code}")
                break

        return items[:self.total_entries]

    @staticmethod
    def extract_converted_price(row):
        return row['convertedCurrentPrice'][0]['__value__']

    def ebay_listings(self):
        active_items = self.find_active_items()
        df = pd.DataFrame(data=active_items)

        df_small = df[['itemId', 'title', 'galleryURL',
                       'viewItemURL', 'sellingStatus']]
        df_small = df_small.applymap(
            lambda x: x[0] if isinstance(x, list) and len(x) == 1 else x)

        df_small['price'] = df_small['sellingStatus'].apply(
            self.extract_converted_price)

        df_small = df_small[['itemId', 'title',
                             'galleryURL', 'viewItemURL', 'price']]
        return df_small


# -------------------------
# SCRAPING
# -------------------------
class EbayScraper:

    def __init__(self, keyword):
        self.keyword = keyword

    @property
    def ebay_url(self):
      return f"https://www.ebay.com/sch/i.html?_from=R40&_nkw={self.keyword}&_sacat=0&rt=nc&LH_Sold=1&LH_Complete=1&_ipg=240"

    def _get_soup(self):
      response = requests.get(self.ebay_url)
      return BeautifulSoup(response.text, 'html.parser')

    def _get_items(self):
      return self._get_soup().find_all("li", class_="s-item s-item__pl-on-bottom")[1:]

    def get_output(self):
      output = []
      for i in self._get_items():
        try:
          clean_item = BookListing(i)
          item_dict = {
              "img_link": clean_item.image_link,
              "title": clean_item.title,
              "price": clean_item.price,
              "reduced": clean_item.reduced,
              "seller": clean_item.seller,
              "seller_rating": clean_item.seller_rating,
              "seller_sales": clean_item.seller_sales,
              "sale_data": clean_item.sale_date,
              "country": clean_item.country,
          }
          output.append(item_dict)
        except:
          pass
      return pd.DataFrame(output)

class BookListing:

    def __init__(self, listing):
        self.listing = listing

    def _find_text(self, tag, class_name, default="Not found"):
        element = self.listing.find(tag, class_=class_name)
        return element.text if element else default

    @property
    def image_link(self):
        img_div = self.listing.find("div", class_="s-item__image-wrapper image-treatment")
        return img_div.find("img")['src'] if img_div else "No image found"

    @property
    def title(self):
        return self._find_text("div", "s-item__title", "No title found")

    @property
    def price(self):
        price = self._find_text("span", "s-item__price", "No price found")
        return float(price.replace('$', '').replace(',', ''))

    @property
    def reduced(self):
        reduced_div = self.listing.find("span", class_="STRIKETHROUGH POSITIVE ITALIC")
        return 1 if reduced_div else 0

    @property
    def seller_info(self):
        return self._find_text("span", "s-item__seller-info-text", "No seller info found")

    @property
    def seller(self):
      return self.seller_info.split(' ')[0]

    @property
    def seller_rating(self):
        match = re.search(r'\(([\d,]+)\)', self.seller_info)
        if match:
            # Return the matched group without commas to parse it as a number later if needed
            return match.group(1).replace(',', '')

    @property
    def seller_sales(self):
            # Match a percentage, including the possibility of decimal points
        match = re.search(r'(\d+(\.\d+)?)%', self.seller_info)
        if match:
            # Convert the percentage to a decimal number
            percentage = float(match.group(1)) / 100
            return percentage

    @property
    def sale_date(self):
        date_string =  self._find_text("div", "s-item__caption--row", "No date of sale found")
        date_string =date_string.replace("Sold Item","")
        date_string = date_string.replace("Sold ","")
        return date_string

    @property
    def country(self): #broken to fix
        return self._find_text("span", "s-item__location s-item__itemLocation", "No country found")