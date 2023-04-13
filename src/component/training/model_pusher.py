from statistics import mode
from src.exception import CustomException
import sys
from src.logger import logger
from src.entity.config_entity import ModelPusherConfig
from src.entity.artifact_entity import ModelPusherArtifact, ModelTrainerArtifact
from src.ml.model.estimator import  AzurePusher,ModelResolver


import os


class ModelPusher:

    def __init__(self, model_trainer_artifact: ModelTrainerArtifact, model_pusher_config: ModelPusherConfig):
        self.model_trainer_artifact = model_trainer_artifact
        self.model_pusher_config = model_pusher_config
        self.azurep=AzurePusher()
        self.model_resolver=ModelResolver()

    def push_model(self) -> str:
        try:
            logger.info(f"{'>>' * 20}Starting model pusher.{'<<' * 20}")
            local_path= self.model_trainer_artifact.model_trainer_ref_artifact.trained_model_file_path
            dir_path = os.path.dirname(local_path)
            #dir_path=f'{dir}/'
            model_dir=self.model_pusher_config.model_dir
            self.azurep.upload_object(azure_dir=model_dir,local_dir=dir_path)

            return self.model_resolver.get_best_model_path()
        except Exception as e:
            raise CustomException(e, sys)

    def initiate_model_pusher(self) -> ModelPusherArtifact:
        try:
            pushed_dir = self.push_model()
            model_pusher_artifact = ModelPusherArtifact(model_pushed_dir=pushed_dir)
            logger.info(f"Model pusher artifact: {model_pusher_artifact}")
            return model_pusher_artifact
        except Exception as e:
            raise CustomException(e, sys)
