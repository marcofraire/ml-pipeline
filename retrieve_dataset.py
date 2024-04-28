import pandas as pd
from config_ml import config_edition_ml, ML_MODELS_DIRECTORY
from ebay_pull import EbayAPI, EbayScraper
from query_db import QueryMLBooks, QueryEbayListings, QueryEbaySalesLinks
from ml_model import image_binary_classifier
from abc import ABC, abstractmethod  

class EbayListingPipeline:
    def __init__(self, db_details, edition_id):
        self.db_details = db_details
        self.edition_id = edition_id

    @abstractmethod
    def retrieve_listings(self):
        pass

    @property
    def edition_ml_model_path(self):
        return f"{ML_MODELS_DIRECTORY}{config_edition_ml[self.edition_id]['ml_model']}"

    @staticmethod
    def is_signed_model(title):
        if 'signed' in title.lower():
            return 'Signed', 1
        else:
            return 'Not Signed', 0

    def predict_edition(self, df):
        df['is_edition'], df['is_edition_probability'] = zip(
            *df.apply(lambda x: image_binary_classifier(self.edition_ml_model_path, x['galleryURL']), axis=1))
        return df

    def predict_signed(self, df):
        df['signed'], df['is_signed_probability'] = zip(
            *df.apply(lambda x: self.is_signed_model(x['title']), axis=1))
        return df

    def predict_condition(self, df):
        df['condition'], df['condition_probability'] = 'Not Available', 0
        return df

    def predict_sub_edition(self, df):
        df['sub_edition'], df['sub_edition_probability'] = 'Not Available', 0
        return df

    def dataset_with_predictions(self):
        df = self.retrieve_listings()
        df = self.predict_edition(df)
        df = self.predict_signed(df)
        df = self.predict_condition(df)
        df = self.predict_sub_edition(df)
        return df
class NewEbayListingsPipeline(EbayListingPipeline):
    def __init__(self, db_details, edition_id, app_id):
        super().__init__(db_details, edition_id)
        self.app_id = app_id



    def retrieve_listings(self):
        df_ebay = EbayAPI(
            self.app_id, config_edition_ml[self.edition_id]['ebay_api_keywords']).ebay_listings()

        df_db = QueryMLBooks(self.db_details, self.edition_id).query_db()
        df_total = pd.merge(
            df_ebay, df_db['img_link'], left_on='galleryURL', right_on='img_link', how='left')
        df_total = df_total[df_total['img_link'].isna()]
        df_total['edition_id'] = self.edition_id
        df_total.drop(['img_link'], axis=1, inplace=True)
        return df_total


class NewEbaySalesPipeline(EbayListingPipeline):

    @property
    def keyword(self):
        keyword = config_edition_ml[self.edition_id]['ebay_api_keywords']
        return keyword.replace(" ", "+")

    def retrieve_listings(self):

        df_ebay = EbayScraper(self.keyword).get_output()

        df_db = QueryEbaySalesLinks(
            self.db_details, self.edition_id).query_db()
        df_total = pd.merge(df_ebay, df_db, left_on='img_link',
                            right_on='img_link_db', how='left')
        df_total = df_total[df_total['img_link_db'].isna()]
        df_total.drop(['img_link_db'], axis=1, inplace=True)

        # check if actual useful
        df_ebay_listings = QueryEbayListings(
            self.db_details, self.edition_id).query_db()
        df_total = pd.merge(df_total, df_ebay_listings,
                            on='img_link', how='left')
        df_total['correct'] = df_total['edition_id'].notna()
        df_total.drop(['edition_id'], axis=1, inplace=True)

        # ML Books
        df_ml_books = QueryMLBooks(self.db_details, self.edition_id).query_db()
        df_total = pd.merge(df_total, df_ml_books, on='img_link', how='left')
        df_total['edition_id'] = self.edition_id
        # As I am checking already in DB and here i should only have negatives
        df_total = df_total[df_total['label'].isna()]
        df_total.rename(columns = {'img_link': 'galleryURL'}, inplace = True)

        return df_total
