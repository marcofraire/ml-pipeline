import psycopg2
from query_db import QueryImageFeatures, QueryListingsMissingEdition
from torch_model import extract_features, find_closest_image


def _insert_query_constructor(df):
    # SQL to create and populate a temporary table
    insert_sql = """
    DROP TABLE IF EXISTS temp_updates;
    CREATE TEMP TABLE temp_updates (
        img_id VARCHAR,
        edition_id INT
    );
    INSERT INTO temp_updates (img_id, edition_id) VALUES
    """

    # Construct values for insertion into the temporary table
    values_list = []
    for index, row in df.iterrows():
        row_values = f"('{row['img_id']}', {row['edition_id']})"
        values_list.append(row_values)

    values_sql = ",\n      ".join(values_list)

    # SQL to update the main table using the temporary table
    update_sql = """
    ;
    UPDATE bbourse.book_listings
    SET edition_id = temp_updates.edition_id
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


def find_load_editions(db_details, hard_limit= None):

    df_features = QueryImageFeatures(db_details).query_db()
    df_listings = QueryListingsMissingEdition(db_details).query_db()
    if hard_limit is not None:
        df_listings = df_listings.head(hard_limit)

    df_listings['feature_vector'] = df_listings['img_link'].apply(
        lambda link: extract_features(link))

    list_images = df_features['feature_vector'].to_list()
    list_editions = df_features['edition_id'].to_list()

    df_listings['edition_id'] = df_listings['feature_vector'].apply(
        lambda link: find_closest_image(link, list_images, list_editions))

    df_to_load = df_listings[['img_id', 'edition_id']]
    batch_process_df_book_listings(db_details, df_to_load)
