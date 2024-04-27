import requests
import pandas as pd

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
