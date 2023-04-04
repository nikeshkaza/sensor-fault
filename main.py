import os
import argparse
from src.exception import CustomException
from src.pipeline.training import TrainingPipeline
from src.logger import logger
from src.config.pipeline.training import SensorConfig
import sys


def start_training(start=False):
    try:
        if not start:
            return None
        print("Training Running")
        TrainingPipeline(SensorConfig()).start()
        
    except Exception as e:
        raise CustomException(e, sys)


def start_prediction(start=False):
    try:
        if not start:
            return None
        print("Prediction started")
        PredictionPipeline().start_batch_prediction()
        
    except Exception as e:
        raise CustomException(e, sys)


def main(training_status, prediction_status):
    try:

        start_training(start=training_status)
        start_prediction(start=prediction_status)
    except Exception as e:
        raise CustomException(e, sys)


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--t", default=1, type=int, help="If provided true training will be done else not")
        parser.add_argument("--p", default=0, type=int, help="If provided prediction will be done else not")

        args = parser.parse_args()

        main(training_status=args.t, prediction_status=args.p)
    except Exception as e:
        print(e)
        pass
        logger.exception(CustomException(e, sys))
