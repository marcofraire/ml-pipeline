from blob import list_blob_urls
from load_file import prepare_and_send_data
from query_db import QueryAllEditionImageLinks
import pandas as pd


def load_missing_editions(db_details, connection_string, env ='production'):
    container_name = 'edition-covers'
    all_blob_urls = list_blob_urls(connection_string, container_name)

    df = QueryAllEditionImageLinks(db_details).query_db()
    images_in_db = df['image_link'].to_list()

    missing_images = [x for x in all_blob_urls if x not in images_in_db]

    missing_images_dict = [{'image': x} for x in missing_images]
    data = {'edition_details': missing_images_dict}
    df = pd.DataFrame(data)
    df['display'] = False

    prepare_and_send_data(df, 'book_editions', env=env)
