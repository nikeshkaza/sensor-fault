import os

PIPELINE_NAME = "sensor-fault"
PIPELINE_ARTIFACT_DIR = os.path.join(os.getcwd(), "sensor_fault_artifact")

SCHEMA_FILE_PATH = os.path.join("src","constant","training_pipeline_config", "schema.yaml")
TARGET_COLUMN = "class"

#from constant.training_pipeline_config.data_ingestion import *