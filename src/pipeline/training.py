from src.config.pipeline.training import SensorConfig
from src.exception import CustomException
from src.component.training.data_ingestion import DataIngestion

from src.entity.artifact_entity import DataIngestionArtifact
#from constant.s3bucket import TRAINING_BUCKET_NAME,TRAINING_LOG_NAME
from src.constant import TIMESTAMP
from src.logger import LOG_FILE_PATH,LOG_DIR
#from cloud_storage.s3_syncer import S3Sync
import sys,os


class TrainingPipeline:

    def __init__(self, Sensor_config: SensorConfig):
        self.insurance_config: SensorConfig = Sensor_config
        #self.s3_sync=S3Sync()

    def start_data_ingestion(self) -> DataIngestionArtifact:
        try:
            data_ingestion_config = self.insurance_config.get_data_ingestion_config()
            data_ingestion = DataIngestion(data_ingestion_config=data_ingestion_config)
            data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
            return data_ingestion_artifact

        except Exception as e:
            raise CustomException(e, sys)
        

    def start(self):
        try:
            data_ingestion_artifact = self.start_data_ingestion()
            
            
        except Exception as e:
            raise CustomException(e, sys)