from typing import List
from src.exception import CustomException
from sklearn.metrics import f1_score,precision_score,recall_score
import os,sys


def get_classification_score(y_true,y_pred)-> List[float]:
    try:
        scores=[]
        model_f1_score = f1_score(y_true, y_pred)
        model_recall_score = recall_score(y_true, y_pred)
        model_precision_score=precision_score(y_true,y_pred)

        scores.append(model_f1_score)
        scores.append(model_precision_score)
        scores.append(model_recall_score)

        return scores
    except Exception as e:
        raise CustomException(e,sys)