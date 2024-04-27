import pandas as pd
import requests
import json
from datetime import datetime
from config_load_db import load_db_configurations


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

        print(json.dumps(payload, indent=2))
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code != 200:
            print(
                f"Failed to send data. Status code: {response.status_code}, Response: {response.text}"
            )
        else:
            print(f"Successfully sent data.")
