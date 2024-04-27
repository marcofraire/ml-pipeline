import pandas as pd
from config_ml import config_edition_ml, ML_MODELS_DIRECTORY
from ebay_pull import EbayAPI
from query_db import QueryMLBooks
from ml_model import image_binary_classifier

class NewEbayListings:
    def __init__(self, db_details, app_id, edition_id):
        self.db_details = db_details
        self.app_id = app_id
        self.edition_id = edition_id

    @property
    def edition_ml_model_path(self):
        return f"{ML_MODELS_DIRECTORY}{config_edition_ml[self.edition_id]['ml_model']}"

    def retrieve_new_ebay_listings(self):
        df_ebay = EbayAPI(
            self.app_id, config_edition_ml[self.edition_id]['ebay_api_keywords']).ebay_listings()

        df_db = QueryMLBooks(self.db_details, self.edition_id).query_db()
        df_total = pd.merge(
            df_ebay, df_db['img_link'], left_on='galleryURL', right_on='img_link', how='left')
        df_total = df_total[df_total['img_link'].isna()]
        df_total['edition_id'] = self.edition_id
        df_total.drop(['img_link'], axis=1, inplace=True)
        return df_total

    @staticmethod
    def is_signed_model(title):
        if 'signed' in title.lower():
            return 'Signed', 1
        else:
            return 'Not Signed', 0

    def predict_edition(self, df):
        df['is_edition'], df['is_edition_probability'] = zip(*df.apply(lambda x: image_binary_classifier(self.edition_ml_model_path, x['galleryURL']), axis=1))
        return df

    def predict_signed(self, df):
        df['signed'] , df['is_signed_probability']= zip(*df.apply(lambda x: self.is_signed_model(x['title']), axis=1))
        return df

    def predict_condition(self, df):
        df['condition'], df['condition_probability'] = 'Not Available' , 0
        return df

    def predict_sub_edition(self, df):
        df['sub_edition'], df['sub_edition_probability'] = 'Not Available' , 0
        return df

    def dataset_with_predictions(self):
        df = self.retrieve_new_ebay_listings()
        df = self.predict_edition(df)
        df = self.predict_signed(df)
        df = self.predict_condition(df)
        df = self.predict_sub_edition(df)
        return df