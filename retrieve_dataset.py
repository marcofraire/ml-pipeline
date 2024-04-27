import pandas as pd
from config_ml import config_edition_ml
from ebay_pull import EbayAPI
from query_db import QueryMLBooks

def retrieve_new_ebay_listings(db_details, app_id, edition_id):
  df_ebay = EbayAPI(app_id, config_edition_ml[edition_id]['ebay_api_keywords']).ebay_listings()
  
  df_db = QueryMLBooks(db_details, edition_id).query_db()
  df_total = pd.merge(df_ebay, df_db['img_link'], left_on ='galleryURL', right_on ='img_link', how='left')
  df_total = df_total[df_total['img_link'].isna()]
  df_total['edition_id'] = edition_id
  df_total.drop(['img_link'], axis=1, inplace=True)
  return df_total