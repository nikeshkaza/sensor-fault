from src.utils import SensorData #load_numpy, save_object, load_object
from src.exception import CustomException
from src.logger import logger
from src.entity.artifact_entity import DataTransformationArtifact,ModelTrainerArtifact,PartialModelTrainerMetricArtifact,PartialModelTrainerRefArtifact
from src.entity.config_entity import ModelTrainerConfig
import os,sys
from xgboost import XGBClassifier
from src.ml.metric.classification_metric import get_classification_score
from src.ml.model.estimator import SensorModel
from src.utils import SensorData


class ModelTrainer:

    def __init__(self,model_trainer_config:ModelTrainerConfig,
        data_transformation_artifact:DataTransformationArtifact):
        try:
            logger.info(f"{'>>' * 20}Starting model trainer.{'<<' * 20}")
            self._sensor_config=SensorData()
            self.model_trainer_config=model_trainer_config
            self.data_transformation_artifact=data_transformation_artifact
        except Exception as e:
            raise CustomException(e,sys)
        
    def perform_hyper_paramter_tunig(self):
        pass

    def train_model(self,x_train,y_train):
        try:
            xgb_clf = XGBClassifier()
            xgb_clf.fit(x_train,y_train)
            return xgb_clf
        except Exception as e:
            raise CustomException(e,sys)

    

    def initiate_model_training(self) -> ModelTrainerArtifact:

        try:
            train_file_path = self.data_transformation_artifact.transformed_train_file_path
            test_file_path = self.data_transformation_artifact.transformed_test_file_path

            #loading training array and testing array
            train_arr = self._sensor_config.load_numpy_array_data(train_file_path)
            test_arr = self._sensor_config.load_numpy_array_data(test_file_path)

            x_train, y_train, x_test, y_test = (
                train_arr[:, :-1],
                train_arr[:, -1],
                test_arr[:, :-1],
                test_arr[:, -1],
            )

            model = self.train_model(x_train, y_train)
            y_train_pred = model.predict(x_train)
            classification_train_metric =  get_classification_score(y_true=y_train, y_pred=y_train_pred)
            train_metric_artifact = PartialModelTrainerMetricArtifact(f1_score=classification_train_metric[0],
                                                                      precision_score=classification_train_metric[1],
                                                                      recall_score=classification_train_metric[2])
            logger.info(f"Model_Trainer train metric: {train_metric_artifact}")

            if train_metric_artifact.f1_score<=self.model_trainer_config.base_accuracy:
                raise Exception("Trained model is not good to provide expected accuracy")

            y_test_pred = model.predict(x_test)
            classification_test_metric = get_classification_score(y_true=y_test, y_pred=y_test_pred)
            
            test_metric_artifact = PartialModelTrainerMetricArtifact(f1_score=classification_test_metric[0],
                                                                     precision_score=classification_test_metric[1],
                                                                     recall_score=classification_test_metric[2])

            logger.info(f"Model_Trainer test metric: {test_metric_artifact}")
            
            #need to compare train f1 score and test f1 score
            #ref_artifact = self.export_trained_model(model=trained_model)


            preprocessor = self._sensor_config.load_object(file_path=self.data_transformation_artifact.exported_pipeline_file_path)
            
            model_dir = os.path.dirname(self.model_trainer_config.trained_model_file_path)
            os.makedirs(model_dir,exist_ok=True)
            sensor_model = SensorModel(preprocessor=preprocessor,model=model)
            self._sensor_config.save_object(self.model_trainer_config.trained_model_file_path, obj=sensor_model)
            model_dir_path=self.model_trainer_config.trained_model_file_path
            model_trainer_artifact = ModelTrainerArtifact(model_trainer_ref_artifact=model_dir_path,
                                                          model_trainer_train_metric_artifact=train_metric_artifact,
                                                          model_trainer_test_metric_artifact=test_metric_artifact)

            logger.info(f"Model trainer artifact: {model_trainer_artifact}")

            return model_trainer_artifact

        except Exception as e:
            raise CustomException(e, sys)
