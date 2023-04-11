import os
from azure.storage.blob import BlobServiceClient#, BlobClient, ContainerClient
from dotenv import load_dotenv
load_dotenv()

CONNECTION_STRING=os.environ.get("CONNECTION_STRING")
CONTAINER_NAME= os.environ.get("CONTAINER_NAME")

class AzureConnectionConfig:
    azure_client=None
    def __init__(self):
        # Create the BlobServiceClient object
        blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)

        # Create the ContainerClient object
        AzureConnectionConfig.azure_client = blob_service_client.get_container_client(CONTAINER_NAME)

        self.azure_client=AzureConnectionConfig.azure_client


        