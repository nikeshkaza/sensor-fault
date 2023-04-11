import os,sys
import pickle
import re
from azure.storage.blob import BlobClient
import pandas as pd
from src.exception import CustomException
from dotenv import load_dotenv
from src.constant.training_pipeline_config.model_evaluation import MODEL_FOLDER
from src.config.azure_connection_config import AzureConnectionConfig,CONNECTION_STRING,CONTAINER_NAME
from src.constant.training_pipeline_config.model_trainer import MODEL_TRAINER_MODEL_NAME

load_dotenv()



class TargetValueMapping:
    def __init__(self):
        self.neg: int = 0
        self.pos: int = 1

    def to_dict(self):
        return self.__dict__

    def reverse_mapping(self):
        mapping_response = self.to_dict()
        return dict(zip(mapping_response.values(), mapping_response.keys()))
    

class SensorModel:

    def __init__(self,preprocessor,model):
        try:
            self.preprocessor = preprocessor
            self.model = model
        except Exception as e:
            raise CustomException(e,sys)
    
    def predict(self,x):
        try:
            x_transform = self.preprocessor.transform(x)
            y_hat = self.model.predict(x_transform)
            return y_hat
        except Exception as e:
            raise CustomException(e,sys)
        

class ModelResolver:
    def __init__(self,model_folder=MODEL_FOLDER,connection_string=CONNECTION_STRING,container_name=CONTAINER_NAME):
        try:
            self.models_folder = model_folder
            self.connection_string=connection_string
            self.container_name=container_name
            self.azurecc=AzureConnectionConfig()

        except Exception as e:
            raise CustomException(e,sys)
        
    def is_model_exists(self):
        try:
            blob_names=[]
            blobs=self.azurecc.azure_client.list_blobs(name_starts_with=self.models_folder)
            for blob in blobs:
                blob_names.append(blob)
            if not len(blob_names)>1:
                return False
            return True

        except Exception as e:
            raise CustomException(e,sys)

    def get_best_model_path(self):
        try:
            blobs = self.azurecc.azure_client.list_blobs(name_starts_with=self.models_folder)
            timestamps = []
            for blob in blobs: 
                tmp_key = blob.name
                timestamp = re.findall(r'\d+', tmp_key)
                timestamps.extend(list(map(int, timestamp)))

            if len(timestamps) == 0:
                print(None)
            timestamp = max(timestamps)
            model_file_name=MODEL_TRAINER_MODEL_NAME
            model_path = f"{self.models_folder}/{timestamp}/{model_file_name}"
            return model_path
        except Exception as e:
            raise CustomException(e,sys)
    
    def load_object(self,model_path):
        try:
            blob_client = BlobClient.from_connection_string(conn_str=self.connection_string,container_name=self.container_name, blob_name=model_path)
            model_bytes = blob_client.download_blob().readall()
            model = pickle.loads(model_bytes)
            return model
        except Exception as e:
            raise Exception(e,sys)

class AzurePusher:
    def __init__(self,connection_string=CONNECTION_STRING,container_name=CONTAINER_NAME):
        self.connection_string=connection_string
        self.container_name=container_name
        self.azurecc=AzureConnectionConfig()
        
    def upload_object(self,azure_dir, local_dir):
        local_dir = local_dir
        azure_directory = azure_dir
        for root, dirs, files in os.walk(local_dir):
            for file in files:
                # Get the local file path
                local_file_path = os.path.join(root, file)

                # Get the blob name
                azure_blob_name = azure_directory + os.path.relpath(local_file_path, local_dir).replace('\\', '/')

                # Upload the file to the blob with the same name
                blob_client = self.azurecc.azure_client.get_blob_client(azure_blob_name)
                with open(local_file_path, "rb") as f:
                    blob_client.upload_blob(f.read())

