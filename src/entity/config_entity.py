from collections import namedtuple
from src.constant.prediction_pipeline_config.file_config import ARCHIVE_DIR, INPUT_DIR, FAILED_DIR, \
    PREDICTION_DIR, REGION_NAME

TrainingPipelineConfig = namedtuple("PipelineConfig", ["pipeline_name", "artifact_dir"])

DataIngestionConfig = namedtuple("DataIngestionConfig", [
                                                         "data_ingestion_dir",
                                                         "download_dir",
                                                         "file_name",
                                                         "feature_store_dir",
                                                         "failed_dir",
                                                         "datasource_url"
                                                         ])


DataValidationConfig = namedtuple('DataValidationConfig', ["accepted_data_dir", "rejected_data_dir", "file_name"])

DataTransformationConfig = namedtuple('DataTransformationConfig', ['file_name', 'export_pipeline_dir',
                                                                   'transformed_train_dir', "transformed_test_dir",
                                                                   "test_size"
                                                                   ])



ModelTrainerConfig = namedtuple("ModelTrainerConfig", ["base_accuracy", "trained_model_file_path", "metric_list"])


ModelEvaluationConfig = namedtuple("ModelEvaluationConfig",
                                   ["model_evaluation_report_file_path", "threshold", "metric_list", "model_dir",
                                    "container_name"])


ModelPusherConfig = namedtuple("ModelPusherConfig", ["model_dir"])