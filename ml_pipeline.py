from db_interaction import prepare_and_send_data
from retrieve_dataset import NewEbayListingsPipeline, NewEbaySalesPipeline
from utils import get_file_paths, move_file_to_folder, get_timestamp
from config_ml import config_edition_ml, PREDICTION_FILES_DIRECTORY, ARCHIVE_FILES_DIRECTORY
import pandas as pd

def create_prediction_files(db_details, app_id, editions, files = ['ebay_listings','ebay_sales']):
   for ed in editions: 
    for f in files:
      if f == 'ebay_listings':
        df = NewEbayListingsPipeline(db_details, ed, app_id).dataset_with_predictions()
        df.to_excel(f"{PREDICTION_FILES_DIRECTORY}listings_{config_edition_ml[ed]['file_name']}_{get_timestamp()}.xlsx")
      elif f == 'ebay_sales':
        df = NewEbaySalesPipeline(db_details, ed).dataset_with_predictions()
        df.to_excel(f"{PREDICTION_FILES_DIRECTORY}sales_{config_edition_ml[ed]['file_name']}_{get_timestamp()}.xlsx")


def load_files_db():
    for f in get_file_paths(PREDICTION_FILES_DIRECTORY):
        df = pd.read_excel(f)
        if "correct" in df.columns:
          if "listings" in f:
              prepare_and_send_data(df, "ml_book", env = 'production' )
              df = df[df['correct']==True]
              prepare_and_send_data(df, "ebay_listings", env = 'production' )
          elif "sales" in f:
              df['sale_data'] = pd.to_datetime(df['sale_data']).dt.strftime('%Y-%m-%d')
              prepare_and_send_data(df, "ml_book", env = 'production' )
              df = df[df['correct']==True]
              prepare_and_send_data(df, "ebay_sales", env = 'production' )
          move_file_to_folder(f, ARCHIVE_FILES_DIRECTORY)
        else:
          pass