from ebay_pull import EbayAPI
import pandas as pd




import psycopg2

def _insert_query_constructor(df):
    insert_sql = "INSERT INTO bbourse.book_listings (img_id, view_item_url, img_link, title, price, last_seen_ebay) VALUES "

    values_list = []
    for index, row in df.iterrows():
        row_values = f"('{row['img_id']}', " \
                    f"'{row['view_item_url']}', " \
                    f"'{row['img_link']}', " \
                    f"'{row['title'].replace('\'', '\'\'')}', " \
                    f"{row['price']}, CURRENT_TIMESTAMP)"
        values_list.append(row_values)

    values_sql = ",\n      ".join(values_list)
    full_sql = insert_sql + values_sql + """
        ON CONFLICT (img_id) DO UPDATE SET
            price = EXCLUDED.price,
            last_seen_ebay = CURRENT_TIMESTAMP
    """
    return  full_sql

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


def scrape_load_book_listings(db_details, app_id, keywords, batch_size=500):
    for k in keywords:
        df = EbayAPI(app_id, k).ebay_listings()
        df.rename(columns={'img_id':'img_id',
                        'viewItemURL':'view_item_url',
                            'galleryURL':'img_link',
                            'price':'price', }, inplace=True)
        df = df[['img_id','view_item_url', 'img_link','title','price']]
        df = df.drop_duplicates(subset=['img_id'])
        batch_process_df_book_listings(db_details, df, batch_size=batch_size)