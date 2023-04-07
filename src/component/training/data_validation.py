from distutils import dir_util
from src.constant.training_pipeline_config.data_validation import SCHEMA_FILE_PATH
from src.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from src.entity.config_entity import DataValidationConfig
from src.exception import CustomException
from src.logger import logger
from src.utils import SensorData
from src.config.pipeline.training import SensorConfig

import pandas as pd
import os,sys
class DataValidation:

    def __init__(self,data_ingestion_artifact:DataIngestionArtifact,
                        data_validation_config:DataValidationConfig):
        try:
            logger.info(f"{'>>' * 20}Starting data validation.{'<<' * 20}")
            self.sensor_data= SensorData()
            self.data_ingestion_artifact=data_ingestion_artifact
            self.data_validation_config=data_validation_config
            self._schema_config = self.sensor_data.read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise  CustomException(e,sys)
    
    def drop_zero_std_columns(self,dataframe):
        pass


    def validate_number_of_columns(self,dataframe:pd.DataFrame)->bool:
        try:
            number_of_columns = len(self._schema_config["columns"])
            len_of_dataframe= len(dataframe.columns)
            logger.info(f"Required number of columns: {number_of_columns}")
            logger.info(f"Data frame has columns: {len(dataframe.columns)}")
            if len_of_dataframe==number_of_columns:
                return True
            return False
        except Exception as e:
            raise CustomException(e,sys)

    def is_numerical_column_exist(self,dataframe:pd.DataFrame)->bool:
        try:
            numerical_columns = self._schema_config["numerical_columns"]
            dataframe_columns = dataframe.columns

            numerical_column_present = True
            missing_numerical_columns = []
            for num_column in numerical_columns:
                if num_column not in dataframe_columns:
                    numerical_column_present=False
                    missing_numerical_columns.append(num_column)
            
            logger.info(f"Missing numerical columns: [{missing_numerical_columns}]")
            return numerical_column_present
        except Exception as e:
            raise CustomException(e,sys)

    @staticmethod
    def read_data(file_path)->pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise CustomException(e,sys)
    
    """
    def detect_dataset_drift(self,base_df,current_df,threshold=0.05)->bool:
        try:
            status=True
            report ={}
            for column in base_df.columns:
                d1 = base_df[column]
                d2  = current_df[column]
                is_same_dist = ks_2samp(d1,d2)
                if threshold<=is_same_dist.pvalue:
                    is_found=False
                else:
                    is_found = True 
                    status=False
                report.update({column:{
                    "p_value":float(is_same_dist.pvalue),
                    "drift_status":is_found
                    
                    }})
            
            drift_report_file_path = self.data_validation_config.drift_report_file_path
            
            #Create directory
            dir_path = os.path.dirname(drift_report_file_path)
            os.makedirs(dir_path,exist_ok=True)
            write_yaml_file(file_path=drift_report_file_path,content=report,)
            return status
        except Exception as e:
            raise SensorException(e,sys)
    """

    def initiate_data_validation(self)->DataValidationArtifact:
        try:
            error_message = ""
            file_path = self.data_ingestion_artifact.feature_store_file_path
            

            #Reading data from train and test file location
            dataframe = DataValidation.read_data(file_path)
            

            #Validate number of columns
            status = self.validate_number_of_columns(dataframe=dataframe)
            if not status:
                error_message=f"{error_message} dataframe does not contain all columns.\n"
            
        

            #Validate numerical columns

            status = self.is_numerical_column_exist(dataframe=dataframe)
            if not status:
                error_message=f"{error_message} dataframe does not contain all numerical columns.\n"
            
            
            if len(error_message)>0:
                raise Exception(error_message)

            #Let check data drift
            #status = self.detect_dataset_drift(base_df=train_dataframe,current_df=test_dataframe)

            os.makedirs(self.data_validation_config.accepted_data_dir, exist_ok=True)
            accepted_file_path = os.path.join(self.data_validation_config.accepted_data_dir,
                                              self.data_validation_config.file_name
                                              )
            dataframe.to_csv(accepted_file_path)

            data_validation_artifact = DataValidationArtifact(accepted_file_path=accepted_file_path,
                                              rejected_dir=self.data_validation_config.rejected_data_dir
                                              )
            logger.info(f"Data validation artifact: [{data_validation_artifact}]")

            return data_validation_artifact
        except Exception as e:
            raise CustomException(e,sys)

"""      
def main():
    try:
        config = SensorConfig()
        data_validation_config = config.get_data_validation_config()
        data_validation = DataValidation(data_validation_config=data_validation_config)
        data_validation.initiate_data_validation()
    except Exception as e:
        raise CustomException(e, sys)


if __name__ == "__main__":
    try:
        main()

    except Exception as e:
        logger.exception(e)
"""