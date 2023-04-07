import os
import re
import sys
import time
import uuid
from collections import namedtuple
from typing import List

import json
import pandas as pd
from pandas import DataFrame
#aa

from src.config.pipeline.training import SensorConfig
from src.constant.training_pipeline_config.data_ingestion import DATABASE_NAME, COLLECTION_NAME
from src.config.mongo_db_connection import MongoDBClient
#from pyspark.sql import SparkSession

from src.entity.artifact_entity import DataIngestionArtifact
from src.entity.config_entity import DataIngestionConfig
from src.exception import CustomException
from src.logger import logger
from src.utils import SensorData
from datetime import datetime
from src.constant.training_pipeline_config.data_validation import SCHEMA_FILE_PATH

DownloadUrl = namedtuple("DownloadUrl", ["url", "file_path" ])


class DataIngestion:
    # Used to download data in chunks.
    def __init__(self, data_ingestion_config: DataIngestionConfig ):
        """
        data_ingestion_config: Data Ingestion config
        n_retry: Number of retry filed should be tried to download in case of failure encountered
        n_month_interval: n month data will be downloded
        """
        try:
            logger.info(f"{'>>' * 20}Starting data ingestion.{'<<' * 20}")
            self.sensor_data= SensorData()
            self.data_ingestion_config = data_ingestion_config
            self.failed_download_urls: List[DownloadUrl] = []
            self._schema_config= self.sensor_data.read_yaml_file(SCHEMA_FILE_PATH)
            #dataframe = dataframe.drop(self._schema_config["drop_columns"],axis=1)

        except Exception as e:
            raise CustomException(e, sys)


    def export_data_into_download_dir(self) -> DataFrame:
        """
        Export mongo db collection record as data frame XX-into feature-XX
        """
        try:
            logger.info("Exporting data from mongodb to feature store")
            sensor_data = SensorData()
            dataframe = sensor_data.export_collection_as_dataframe(collection_name=COLLECTION_NAME)
            data_ingestion_dir = self.data_ingestion_config.data_ingestion_dir 
            file_name = self.data_ingestion_config.file_name     
            download_files_dir=self.data_ingestion_config.download_dir      

            #creating folder
            dir_path = os.path.dirname(data_ingestion_dir)
            download_path=os.path.join(dir_path,download_files_dir)
            os.makedirs(download_path,exist_ok=True)
            
            file_path = os.path.join(dir_path,download_files_dir,file_name)
            dataframe.to_csv(file_path,index=False,header=True)
            return dataframe
        except  Exception as e:
            raise  CustomException(e,sys)

    

    def move_file_to_feature_store(self, ) -> str:
        """
        downloaded files will be converted and merged into single parquet file
        json_data_dir: downloaded json file directory
        data_dir: converted and combined file will be generated in data_dir
        output_file_name: output file name 
        =======================================================================================
        returns output_file_path
        """
        try:
            
            csv_data_dir = self.data_ingestion_config.download_dir
            data_dir = self.data_ingestion_config.feature_store_dir
            output_file_name = self.data_ingestion_config.file_name
            os.makedirs(data_dir, exist_ok=True)
            file_path = os.path.join(data_dir, f"{output_file_name}")
            logger.info(f"CSV file will be created at: {file_path}")
            if not os.path.exists(csv_data_dir):
                return file_path
            for file_name in os.listdir(csv_data_dir):
                csv_file_path = os.path.join(csv_data_dir, file_name)
                logger.debug(f"Converting {csv_file_path} into CSV format at {file_path}")
                df = pd.read_csv(csv_file_path)
                if len(df) > 0:
                    df = df.drop(self._schema_config["drop_columns"],axis=1)
                    df.to_csv(file_path, index=False)

            return file_path
        except Exception as e:
            raise CustomException(e, sys)

    

    


    def initiate_data_ingestion(self) -> DataIngestionArtifact:
        try:
            logger.info(f"Started downloading json file to csv")
            

            self.export_data_into_download_dir()
            
            if os.path.exists(self.data_ingestion_config.download_dir):
                logger.info(f"Converting and combining downloaded json into csv file")
                self.move_file_to_feature_store()
                

            feature_store_file_path = os.path.join(self.data_ingestion_config.feature_store_dir,
                                                   self.data_ingestion_config.file_name)
            artifact = DataIngestionArtifact(
                feature_store_file_path=feature_store_file_path,
                download_dir=self.data_ingestion_config.download_dir

            )

            logger.info(f"Data ingestion artifact: {artifact}")
            return artifact
        except Exception as e:
            raise CustomException(e, sys)


def main():
    try:
        config = SensorConfig()
        data_ingestion_config = config.get_data_ingestion_config()
        data_ingestion = DataIngestion(data_ingestion_config=data_ingestion_config)
        data_ingestion.initiate_data_ingestion()
    except Exception as e:
        raise CustomException(e, sys)


if __name__ == "__main__":
    try:
        main()

    except Exception as e:
        logger.exception(e)