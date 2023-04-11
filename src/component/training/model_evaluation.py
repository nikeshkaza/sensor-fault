
from src.exception import CustomException
from src.logger import logger
from src.entity.artifact_entity import DataValidationArtifact,ModelTrainerArtifact,ModelEvaluationArtifact
from src.entity.config_entity import ModelEvaluationConfig
import os,sys
from src.ml.metric.classification_metric import get_classification_score
from src.ml.model.estimator import SensorModel
from src.utils import SensorData
from src.ml.model.estimator import ModelResolver
from src.constant.training_pipeline_config import TARGET_COLUMN
from src.ml.model.estimator import TargetValueMapping
import pandas  as  pd
class ModelEvaluation:


    def __init__(self,model_eval_config:ModelEvaluationConfig,
                    data_validation_artifact:DataValidationArtifact,
                    model_trainer_artifact:ModelTrainerArtifact):
        
        try:
            self.model_eval_config=model_eval_config
            self.data_validation_artifact=data_validation_artifact
            self.model_trainer_artifact=model_trainer_artifact
        except Exception as e:
            raise CustomException(e,sys)
    


    def evaluate_trained_model(self)->ModelEvaluationArtifact:
        try:
            is_model_accepted, is_active = False, False
            accepted_file_path = self.data_validation_artifact.accepted_file_path

            #valid df
            df = pd.read_csv(accepted_file_path)
            

            y_true = df[TARGET_COLUMN]
            y_true.replace(TargetValueMapping().to_dict(),inplace=True)
            df.drop(TARGET_COLUMN,axis=1,inplace=True)

            train_model_file_path = self.model_trainer_artifact.model_trainer_ref_artifact
            model_resolver = ModelResolver()
            sensor_data=SensorData()
            is_model_accepted=True


            #if not model_resolver.is_model_exists():
            #    model_evaluation_artifact = ModelEvaluationArtifact(
            #        is_model_accepted=is_model_accepted, 
            #        improved_accuracy=None, 
            #        best_model_path=None, 
            #        trained_model_path=train_model_file_path, 
            #        train_model_metric_artifact=self.model_trainer_artifact.test_metric_artifact, 
            #        best_model_metric_artifact=None)
            #    logger.info(f"Model evaluation artifact: {model_evaluation_artifact}")
            #    return model_evaluation_artifact

            latest_model_path = model_resolver.get_best_model_path()
            latest_model = model_resolver.load_object(model_path=latest_model_path)
            train_model = sensor_data.load_object(file_path=train_model_file_path)
            
            y_trained_pred = train_model.predict(df)
            y_latest_pred  =latest_model.predict(df)

            trained_metric = get_classification_score(y_true, y_trained_pred)
            latest_metric = get_classification_score(y_true, y_latest_pred)

            changed_accuracy = trained_metric[0]-latest_metric[0]
            if self.model_eval_config.threshold < changed_accuracy:
                #0.02 < 0.03
                is_model_accepted=True
                is_active=True
            else:
                is_model_accepted=False

            
            model_evaluation_artifact = ModelEvaluationArtifact(
                    model_accepted=is_model_accepted, 
                    changed_accuracy=changed_accuracy, 
                    best_model_path=latest_model_path, 
                    trained_model_path=train_model_file_path, 
                    active=is_active

            )

            model_eval_report = model_evaluation_artifact.__dict__

            #save the report
            #write_yaml_file(self.model_eval_config.report_file_path, model_eval_report)
            logger.info(f"Model evaluation artifact: {model_evaluation_artifact}")
            return model_evaluation_artifact
            
        except Exception as e:
            raise CustomException(e,sys)
        
    def initiate_model_evaluation(self) -> ModelEvaluationArtifact:
        try:
            model_accepted = True
            is_active = True
            _model_resolver=ModelResolver()
            if not _model_resolver.is_model_exists():
                latest_model_path = None
                trained_model_path = self.model_trainer_artifact.model_trainer_ref_artifact.trained_model_file_path
                model_evaluation_artifact = ModelEvaluationArtifact(
                    model_accepted=model_accepted, 
                    changed_accuracy=0.0, 
                    best_model_path=latest_model_path, 
                    trained_model_path=trained_model_path, 
                    active=is_active

            )
            else:
                model_evaluation_artifact = self.evaluate_trained_model()

            logger.info(f"Model evaluation artifact: {model_evaluation_artifact}")
            #self.model_eval_artifact_data.save_eval_artifact(model_eval_artifact=model_evaluation_artifact)
            return model_evaluation_artifact
        except Exception as e:
            raise CustomException(e, sys)

    
    

