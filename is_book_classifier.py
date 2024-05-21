import numpy as np
import torch
import psycopg2
from query_db import QueryListingsMissingIsBook
target_dict = {
    'book': 0,
    'set': 1,
    'no-book': 2
}

rev_dict = {v: k for k, v in target_dict.items()}
from extract_text_features import extract_text_features
from torch_model import extract_features

from is_book_model import get_model

def predict_is_book(img_link, title, model):
    # Extract features from the image
    image_features = extract_features(img_link)
    
    # Extract features from the text
    text_features = extract_text_features(title)
    # Combine the features into a single array
    combined_features = np.hstack((image_features, text_features))
    
    # Convert to PyTorch tensor and add batch dimension
    combined_features = torch.tensor(combined_features, dtype=torch.float32).unsqueeze(0)  # Shape: (1, 1768)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    combined_features = combined_features.to(device)
    
    # Set the model to evaluation mode
    model.eval()
    
    # Perform the forward pass to get the output
    with torch.no_grad():
        output = model(combined_features)
    
    # Get the predicted class
    predicted_class = torch.argmax(output, dim=1).item()
    
    return rev_dict[predicted_class]

def _insert_query_constructor(df):
    # SQL to create and populate a temporary table
    insert_sql = """
    DROP TABLE IF EXISTS temp_updates;
    CREATE TEMP TABLE temp_updates (
        img_id VARCHAR,
        is_book VARCHAR
    );
    INSERT INTO temp_updates (img_id, is_book) VALUES
    """

    # Construct values for insertion into the temporary table
    values_list = []
    for index, row in df.iterrows():
        row_values = f"('{row['img_id']}', '{row['is_book']}')"#different for string and int
        values_list.append(row_values)

    values_sql = ",\n      ".join(values_list)

    # SQL to update the main table using the temporary table
    update_sql = """
    ;
    UPDATE bbourse.book_listings
    SET is_book = temp_updates.is_book
    FROM temp_updates
    WHERE bbourse.book_listings.img_id = temp_updates.img_id;
    DROP TABLE temp_updates;
    """

    # Combine all parts of the SQL
    full_sql = insert_sql + values_sql + update_sql
    return full_sql


def insert_df_book_listings(db_details, df):
    conn_params = {
        'dbname': db_details['NAME'],
        'user': db_details['USER'],
        'password': db_details['PASSWORD'],
        'host': db_details['HOST'],
        'port': db_details['PORT']
    }
    full_sql = _insert_query_constructor(df)
    conn = psycopg2.connect(**conn_params)
    cursor = conn.cursor()

    cursor.execute(full_sql)
    conn.commit()

    cursor.close()
    conn.close()


def batch_process_df_book_listings(db_details, df, batch_size=500):
    # Calculate total number of batches
    num_batches = (len(df) + batch_size - 1) // batch_size

    # Loop through each batch and process it
    for i in range(num_batches):
        batch_start = i * batch_size
        batch_end = min((i + 1) * batch_size, len(df))
        df_batch = df.iloc[batch_start:batch_end]

        # Insert current batch to the database
        insert_df_book_listings(db_details, df_batch)


def find_load_is_book(db_details,connection_string, hard_limit= None):
    model = get_model(connection_string)
    df_listings = QueryListingsMissingIsBook(db_details).query_db()
    if hard_limit is not None:
        df_listings = df_listings.head(hard_limit)

    df_listings['is_book'] = df_listings.apply(
    lambda row: predict_is_book(row['img_link'], row['title'], model),
    axis=1
)

    df_to_load = df_listings[['img_id', 'is_book']]
    batch_process_df_book_listings(db_details, df_to_load)