from typing import Callable, Dict, Tuple, Union
import mlflow
from pandas import Series
from scipy.sparse._csr import csr_matrix
from sklearn.base import BaseEstimator
from utils.sklearn import load_class, tune_hyperparameters

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer


@transformer
def hyperparameter_tuning(
    model_class_name: str,
    training_set: Dict[str, Union[Series, csr_matrix]],
    *args,
    **kwargs,
) -> Tuple[
    Dict[str, Union[bool, float, int, str]],
    csr_matrix,
    Series,
    Callable[..., BaseEstimator],
]:
    X_train, X_val, y_train, y_val, dv, train_year, val_year, use_dv = training_set['build']
    print(train_year)
    model_class = load_class(model_class_name)

    if model_class_name=='linear_model.LinearRegression':
        max_evaluations=1
    else:
        max_evaluations=50
    max_evaluations=max_evaluations
    hyperparameters = tune_hyperparameters(
        model_class=model_class,
        X_train=X_train,
        y_train=y_train,
        X_val=X_val,
        y_val=y_val,
        max_evaluations=max_evaluations,
        random_state=kwargs.get('random_state'),
        dv=dv,
        train_year = train_year,
        val_year = val_year,
        use_dv = use_dv
        )

    return train_year, hyperparameters, dict(cls=model_class, name=model_class_name)
