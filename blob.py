from azure.storage.blob import BlobServiceClient, ContainerClient

def list_blob_urls(connection_string, container_name):
    try:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)

        container_client = blob_service_client.get_container_client(container_name)

        blob_urls = []
        for blob in container_client.list_blobs():
            blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{blob.name}"
            blob_urls.append(blob_url)
        
        return blob_urls
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    
import os

def download_model_from_blob(connection_string, container_name, blob_name, download_file_path):
    # Create a BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Get a container client
    container_client = blob_service_client.get_container_client(container_name)

    # Download the model
    blob_client = container_client.get_blob_client(blob_name)
    with open(download_file_path, "wb") as download_file:
        download_file.write(blob_client.download_blob().readall())
    print(f'Model downloaded from Azure Blob Storage to: {download_file_path}')
