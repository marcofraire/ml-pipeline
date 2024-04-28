import pandas as pd
import requests
import json
from datetime import datetime
from config_load_db import load_db_configurations
from utils import move_file_to_folder, get_file_paths
from abc import ABC, abstractmethod
def prepare_and_send_data(df: pd.DataFrame, load_type: str, env: str = "production"):

    config = load_db_configurations.get(load_type)
    if not config:
        raise ValueError(f"Unsupported load type: {load_type}")

    url = config["url"][env]
    payload_template = config["payload_template"]
    headers = {"Content-Type": "application/json"}

    for _, row in df.iterrows():
        payload = {}
        for key, (column_name, data_type) in payload_template.items():
            value = row[column_name]
            if data_type == "int":
                payload[key] = int(value)
            elif data_type == "float":
                payload[key] = float(value)
            elif data_type == "bool":
                payload[key] = bool(value)
            elif data_type == "date":
                try:
                    date_obj = datetime.strptime(value, "%Y-%m-%d")
                    payload[key] = date_obj.isoformat()
                except ValueError:
                    print(
                        f"Error converting {column_name} to date with value '{value}'"
                    )
            else:
                payload[key] = value

        # print(json.dumps(payload, indent=2))
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code != 200:
            print(
                f"Failed to send data. Status code: {response.status_code}, Response: {response.text}"
            )
        else:
            print(f"Successfully sent data.")




class LoadFile:
    def __init__(self, df, env ):
        self.df = df
        self.env = env
    
    def is_edited(self):
        if "correct" in self.df.columns:
            return True
        else:
            return False
    
    @property
    def df_positives(self):
        return self.df[self.df["correct"] == True]

    def preprocess_file(self):
        pass
    
    def load_ml_books(self):
        prepare_and_send_data(self.df, "ml_book", env = self.env)
    
    @abstractmethod
    def load_positive_table(self):
        pass 

    def load_db(self):
        if self.is_edited():
            self.preprocess_file()
            self.load_ml_books()
            self.load_positive_table()
        pass

class EbayListingsLoad(LoadFile):
    def load_positive_table(self):
        prepare_and_send_data(self.df_positives, "ebay_listings", env = self.env) 

class EbaySalesLoad(LoadFile):
    def preprocess_file(self):
        self.df['sale_data'] = pd.to_datetime(self.df['sale_data']).dt.strftime('%Y-%m-%d')

    def load_positive_table(self):
        prepare_and_send_data(self.df_positives, "ebay_sales", env = self.env) 