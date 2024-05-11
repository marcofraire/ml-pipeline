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