import sys

import numpy as np
import pandas as pd
from imblearn.combine import SMOTETomek
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import RobustScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split


from src.constant.training_pipeline_config.data_transformation import *
from src.entity.artifact_entity import (
    DataTransformationArtifact,
    DataValidationArtifact,
)
from src.entity.config_entity import DataTransformationConfig
from src.exception import CustomException
from src.logger import logger
from src.ml.model.estimator import TargetValueMapping
from src.utils import SensorData
from src.constant.training_pipeline_config import TARGET_COLUMN




class DataTransformation:
    def __init__(self,data_validation_artifact: DataValidationArtifact, 
                    data_transformation_config: DataTransformationConfig,):
        """

        :param data_validation_artifact: Output reference of data ingestion artifact stage
        :param data_transformation_config: configuration for data transformation
        """
        try:
            self.sensor_data=SensorData()
            self.data_validation_artifact = data_validation_artifact
            self.data_transformation_config = data_transformation_config

        except Exception as e:
            raise CustomException(e, sys)


    @staticmethod
    def read_data(file_path) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise CustomException(e, sys)


    @classmethod
    def get_data_transformer_object(cls)->Pipeline:
        try:
            robust_scaler = RobustScaler()
            simple_imputer = SimpleImputer(strategy="constant", fill_value=0)
            preprocessor = Pipeline(
                steps=[
                    ("Imputer", simple_imputer), #replace missing values with zero
                    ("RobustScaler", robust_scaler) #keep every feature in same range and handle outlier
                    ]
            )
            
            return preprocessor

        except Exception as e:
            raise CustomException(e, sys) from e

    
    def initiate_data_transformation(self,) -> DataTransformationArtifact:
        try:
            filepath=self.data_validation_artifact.accepted_file_path
            df = DataTransformation.read_data(file_path=filepath)
            train_df, test_df = train_test_split(df, test_size=DATA_TRANSFORMATION_TEST_SIZE, random_state=42)
            #train_df = DataTransformation.read_data(self.data_validation_artifact.valid_train_file_path)
            #test_df = DataTransformation.read_data(self.data_validation_artifact.valid_test_file_path)
            preprocessor = self.get_data_transformer_object()


            #training dataframe
            input_feature_train_df = train_df.drop(columns=[TARGET_COLUMN], axis=1)
            target_feature_train_df = train_df[TARGET_COLUMN]
            target_feature_train_df = target_feature_train_df.replace( TargetValueMapping().to_dict())

            #testing dataframe
            input_feature_test_df = test_df.drop(columns=[TARGET_COLUMN], axis=1)
            target_feature_test_df = test_df[TARGET_COLUMN]
            target_feature_test_df = target_feature_test_df.replace(TargetValueMapping().to_dict())

            preprocessor_object = preprocessor.fit(input_feature_train_df)
            transformed_input_train_feature = preprocessor_object.transform(input_feature_train_df)
            transformed_input_test_feature =preprocessor_object.transform(input_feature_test_df)

            smt = SMOTETomek(sampling_strategy="minority")

            input_feature_train_final, target_feature_train_final = smt.fit_resample(
                transformed_input_train_feature, target_feature_train_df
            )

            input_feature_test_final, target_feature_test_final = smt.fit_resample(
                transformed_input_test_feature, target_feature_test_df
            )

            train_arr = np.c_[input_feature_train_final, np.array(target_feature_train_final) ]

            test_arr = np.c_[ input_feature_test_final, np.array(target_feature_test_final) ]

            #save numpy array data
            self.sensor_data.save_numpy_array_data( self.data_transformation_config.transformed_train_dir, train_arr )
            self.sensor_data.save_numpy_array_data( self.data_transformation_config.transformed_test_dir,test_arr)
            self.sensor_data.save_object( self.data_transformation_config.export_pipeline_dir, preprocessor_object)
            
            
            #preparing artifact
            data_transformation_artifact = DataTransformationArtifact(
                exported_pipeline_file_path=self.data_transformation_config.export_pipeline_dir,
                transformed_train_file_path=self.data_transformation_config.transformed_train_dir,
                transformed_test_file_path=self.data_transformation_config.transformed_test_dir
            )
            logger.info(f"Data transformation artifact: {data_transformation_artifact}")
            return data_transformation_artifact
        except Exception as e:
            raise CustomException(e, sys) from e

"""
if __name__ == "__main__":
    try:
        data_validation_artifact = DataValidationArtifact
        data_transformation_config = DataTransformationConfig

        # Create an instance of the DataTransformation class
        data_transformation = DataTransformation(data_validation_artifact, data_transformation_config)

        # Call the initiate_data_transformation method
        data_transformation.initiate_data_transformation()

    except Exception as e:
        logger.exception(e)
"""