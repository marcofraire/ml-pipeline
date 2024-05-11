from ebay_pull import EbayAPI
from config_ml import config_edition_ml
from utils import get_timestamp

def pull_ebay_images(app_id, edition_id, destination_folder, total_entries = 1000):
    df = EbayAPI(app_id, config_edition_ml[edition_id]['ebay_api_keywords'], total_entries).ebay_listings()
    df = df[['img_id','galleryURL', 'title','viewItemURL']]
    df.to_excel(f'{destination_folder}/ebay_images_{get_timestamp()}.xlsx', index=False)
    return df