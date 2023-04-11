import os,sys
from src.exception import CustomException
from src.logger import logger
from src.constant.training_pipeline_config import PIPELINE_NAME,PIPELINE_ARTIFACT_DIR
from src.constant import TIMESTAMP
from src.entity.config_entity import TrainingPipelineConfig,DataIngestionConfig,DataValidationConfig,DataTransformationConfig, ModelTrainerConfig, ModelEvaluationConfig, ModelPusherConfig
from src.constant.training_pipeline_config.data_ingestion import *
from src.constant.training_pipeline_config.data_validation import *
from src.constant.training_pipeline_config.data_transformation import *
from src.constant.training_pipeline_config.model_trainer import *
from src.constant.training_pipeline_config.model_evaluation import *
from src.constant.training_pipeline_config.model_pusher import *
from src.config.azure_connection_config import CONTAINER_NAME


class SensorConfig:

    def __init__(self, pipeline_name=PIPELINE_NAME, timestamp=TIMESTAMP):
        """
        Organization: iNeuron Intelligence Private Limited

        """
        self.timestamp = timestamp
        self.pipeline_name = pipeline_name
        self.pipeline_config = self.get_pipeline_config()

    def get_pipeline_config(self) -> TrainingPipelineConfig:
        """
        This function will provide pipeline config information


        returns > PipelineConfig = namedtuple("PipelineConfig", ["pipeline_name", "artifact_dir"])
        """
        try:
            artifact_dir = PIPELINE_ARTIFACT_DIR
            pipeline_config = TrainingPipelineConfig(pipeline_name=self.pipeline_name,
                                                     artifact_dir=artifact_dir)

            logger.info(f"Pipeline configuration: {pipeline_config}")

            return pipeline_config
        except Exception as e:
            raise CustomException(e, sys)

    def get_data_ingestion_config(self)-> DataIngestionConfig:

        """
        master directory for data ingestion
        we will store metadata information and ingested file to avoid redundant download
        """
        data_ingestion_master_dir = os.path.join(self.pipeline_config.artifact_dir,
                                                 DATA_INGESTION_DIR)

        # time based directory for each run
        data_ingestion_dir = os.path.join(data_ingestion_master_dir,
                                          self.timestamp)


        data_ingestion_config = DataIngestionConfig(
            data_ingestion_dir=data_ingestion_dir,
            download_dir=os.path.join(data_ingestion_dir, DATA_INGESTION_DOWNLOADED_DATA_DIR),
            file_name=DATA_INGESTION_FILE_NAME,
            feature_store_dir=os.path.join(data_ingestion_master_dir, DATA_INGESTION_FEATURE_STORE_DIR),
            failed_dir=os.path.join(data_ingestion_dir, DATA_INGESTION_FAILED_DIR),
            datasource_url=DATA_INGESTION_DATA_SOURCE_URL

        )
        logger.info(f"Data ingestion config: {data_ingestion_config}")
        return data_ingestion_config
    


    def get_data_validation_config(self) -> DataValidationConfig:
        """

        """
        try:
            data_validation_dir = os.path.join(self.pipeline_config.artifact_dir,
                                               DATA_VALIDATION_DIR, self.timestamp)

            accepted_data_dir = os.path.join(data_validation_dir, DATA_VALIDATION_ACCEPTED_DATA_DIR)
            rejected_data_dir = os.path.join(data_validation_dir, DATA_VALIDATION_REJECTED_DATA_DIR)

            data_preprocessing_config = DataValidationConfig(
                accepted_data_dir=accepted_data_dir,
                rejected_data_dir=rejected_data_dir,
                file_name=DATA_VALIDATION_FILE_NAME
            )

            logger.info(f"Data preprocessing config: {data_preprocessing_config}")

            return data_preprocessing_config
        except Exception as e:
            raise CustomException(e, sys)
        
    def get_data_transformation_config(self) -> DataTransformationConfig:
        try:
            data_transformation_dir = os.path.join(self.pipeline_config.artifact_dir,
                                                   DATA_TRANSFORMATION_DIR, self.timestamp)

            transformed_train_data_dir = os.path.join(
                data_transformation_dir, DATA_TRANSFORMATION_TRAIN_DIR
            )
            transformed_test_data_dir = os.path.join(
                data_transformation_dir, DATA_TRANSFORMATION_TEST_DIR
            )

            export_pipeline_dir = os.path.join(
                data_transformation_dir, DATA_TRANSFORMATION_PIPELINE_DIR, DATA_TRANSFORMATION_FILE_NAME
            )
            data_transformation_config = DataTransformationConfig(
                export_pipeline_dir=export_pipeline_dir,
                transformed_test_dir=transformed_test_data_dir,
                transformed_train_dir=transformed_train_data_dir,
                file_name=DATA_TRANSFORMATION_FILE_NAME,
                test_size=DATA_TRANSFORMATION_TEST_SIZE,
            )

            logger.info(f"Data transformation config: {data_transformation_config}")
            return data_transformation_config
        except Exception as e:
            raise CustomException(e, sys)
        
    def get_model_trainer_config(self) -> ModelTrainerConfig:
        try:
            model_trainer_dir = os.path.join(self.pipeline_config.artifact_dir,
                                             MODEL_TRAINER_DIR, self.timestamp)
            trained_model_file_path = os.path.join(
                model_trainer_dir, MODEL_TRAINER_TRAINED_MODEL_DIR, MODEL_TRAINER_MODEL_NAME
            )
            
            model_trainer_config = ModelTrainerConfig(base_accuracy=MODEL_TRAINER_BASE_ACCURACY,
                                                      trained_model_file_path=trained_model_file_path,
                                                      metric_list=MODEL_TRAINER_MODEL_METRIC_NAMES
                                                      )
            logger.info(f"Model trainer config: {model_trainer_config}")
            return model_trainer_config
        except Exception as e:
            raise CustomException(e, sys)
        

    def get_model_evaluation_config(self) -> ModelEvaluationConfig:
        try:
            model_evaluation_dir = os.path.join(self.pipeline_config.artifact_dir,
                                                MODEL_EVALUATION_DIR)

            model_evaluation_report_file_path = os.path.join(
                model_evaluation_dir, MODEL_EVALUATION_REPORT_DIR, MODEL_EVALUATION_REPORT_FILE_NAME
            )

            model_evaluation_config = ModelEvaluationConfig(
                container_name=CONTAINER_NAME,
                model_dir=MODEL_FOLDER,
                model_evaluation_report_file_path=model_evaluation_report_file_path,
                threshold=MODEL_EVALUATION_THRESHOLD_VALUE,
                metric_list=MODEL_EVALUATION_METRIC_NAMES,

            )
            logger.info(f"Model evaluation config: [{model_evaluation_config}]")
            return model_evaluation_config

        except Exception as e:
            raise CustomException(e, sys)
        

    def get_model_pusher_config(self) -> ModelPusherConfig:
        try:
            model_pusher_config = ModelPusherConfig(
                model_dir=MODEL_PUSHER_DIR,
            )
            logger.info(f"Model pusher config: {model_pusher_config}")
            return model_pusher_config
        except  Exception as e:
            raise CustomException(e, sys)