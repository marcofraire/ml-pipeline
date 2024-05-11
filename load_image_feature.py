# -----------------
# Pull images
# -----------------


from torch_model import extract_features
from query_db import QueryBookEditionNoFeature
from load_file import prepare_and_send_data

def load_image_features(DB_DETAILS, env='production'):
    df = QueryBookEditionNoFeature(DB_DETAILS).query_db()
    df['feature_vector'] = df['image_link'].apply(lambda link: extract_features(link))
    df['binding'] = 'Not Available'
    df['edition_metadata'] = 'Not Available'
    prepare_and_send_data(df, load_type='image_features' , env=env)