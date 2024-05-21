from ebay_pull import EbayAPI
from config_ml import ML_MODELS_DIRECTORY, config_edition_ml
from utils import get_timestamp, download_and_save_image,   move_images
import pandas as pd

def pull_ebay_images(app_id, edition_id, total_entries = 1000):
    df = EbayAPI(app_id, config_edition_ml[edition_id]['ebay_api_keywords'], total_entries).ebay_listings()
    df = df[['img_id','galleryURL', 'title','viewItemURL']]
    df.to_excel(f'{ML_MODELS_DIRECTORY}/{edition_id}/Images/ebay_images_{get_timestamp()}.xlsx', index=False)
    return df

def save_images(file_name, edition_id):
  path = f'{ML_MODELS_DIRECTORY}/{edition_id}/Images/{file_name}.xlsx'
  print(path)
  df = pd.read_excel(path)
  folder = f'{ML_MODELS_DIRECTORY}/{edition_id}/Images/Train/'
  for index, row in df.iterrows():
      image_url = row['galleryURL']  
      label = row['folder']  
      img_id = row['img_id']  

      image_name = f"{img_id}.jpg"  # Unique image name

      download_and_save_image(image_url, label, image_name, folder)

def move_images_to_test(edition_id, percentage):
  train_dir = f'{ML_MODELS_DIRECTORY}{edition_id}/Images/Train/'
  test_dir = f'{ML_MODELS_DIRECTORY}{edition_id}/Images/Test/'
  move_images(train_dir, test_dir, percentage)
