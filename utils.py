import datetime
from pathlib import Path

import shutil
import os
def get_timestamp():
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    return timestamp


def get_file_paths(directory):
    path = Path(directory)
    file_paths = [str(file) for file in path.iterdir() if file.is_file()]
    return file_paths


def move_file_to_folder(source_file, destination_folder):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    destination_file = os.path.join(destination_folder, os.path.basename(source_file))
    
    shutil.move(source_file, destination_file)