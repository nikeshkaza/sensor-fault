import os
from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URL = os.environ.get('MONGO_DB_URL')


DATA_INGESTION_DIR = "data_ingestion"
DATA_INGESTION_DOWNLOADED_DATA_DIR = "downloaded_files"
DATA_INGESTION_FILE_NAME = "sensor.csv"
DATA_INGESTION_FEATURE_STORE_DIR = "feature_store"
DATA_INGESTION_FAILED_DIR = "failed_downloaded_files"
DATA_INGESTION_DATA_SOURCE_URL = MONGO_DB_URL
DATABASE_NAME = "Neuron"
COLLECTION_NAME = "sensor"


