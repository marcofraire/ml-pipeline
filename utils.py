import datetime
from pathlib import Path
import requests
import shutil
import os
from random import sample


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

def download_and_save_image(image_url, folder_name, image_name, base_directory):
    full_folder_path = os.path.join(base_directory, folder_name)

    os.makedirs(full_folder_path, exist_ok=True)

    image_path = os.path.join(full_folder_path, image_name)

    response = requests.get(image_url)
    if response.status_code == 200:
        with open(image_path, 'wb') as f:
            f.write(response.content)
    else:
        print(f"Failed to download {image_url}")

def move_images(source_dir, target_dir, percentage):
    for root, dirs, files in os.walk(source_dir):
        image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

        num_to_move = len(image_files) * percentage // 100

        selected_files = sample(image_files, num_to_move)

        relative_path = os.path.relpath(root, source_dir)
        target_folder = os.path.join(target_dir, relative_path)

        os.makedirs(target_folder, exist_ok=True)

        for file_name in selected_files:
            src_file_path = os.path.join(root, file_name)
            dest_file_path = os.path.join(target_folder, file_name)
            shutil.move(src_file_path, dest_file_path)

            print(f'Moved {src_file_path} to {dest_file_path}')
