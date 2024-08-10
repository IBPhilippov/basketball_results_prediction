from typing import Callable, Dict, Optional, Tuple, Union

import numpy as np
import sklearn
from hyperopt import STATUS_OK, Trials, fmin, hp, tpe
from pandas import Series
from scipy.sparse._csr import csr_matrix
from sklearn.base import BaseEstimator
from sklearn.metrics import mean_squared_error
import mlflow
from utils.shared import build_hyperparameters_space
import pickle
import os

HYPERPARAMETERS_WITH_CHOICE_INDEX = [
 #   'fit_intercept',
]


def load_class(module_and_class_name: str) -> BaseEstimator:
    """
    module_and_class_name:
        ensemble.ExtraTreesRegressor
        ensemble.GradientBoostingRegressor
        ensemble.RandomForestRegressor
        linear_model.Lasso
        linear_model.LinearRegression
        svm.LinearSVR
    """
    parts = module_and_class_name.split('.')
    cls = sklearn
    for part in parts:
        cls = getattr(cls, part)

    return cls


def train_model(
    model: BaseEstimator,
    X_train: csr_matrix,
    y_train: Series,
    X_val: Optional[csr_matrix] = None,
    eval_metric: Callable = mean_squared_error,
    fit_params: Optional[Dict] = None,
    y_val: Optional[Series] = None,
    **kwargs,
) -> Tuple[BaseEstimator, Optional[Dict], Optional[np.ndarray]]:
    model.fit(X_train, y_train, **(fit_params or {}))

    metrics = None
    y_pred = None
    if X_val is not None and y_val is not None:
        y_pred = model.predict(X_val)

        rmse = eval_metric(y_val, y_pred, squared=False)
        mse = eval_metric(y_val, y_pred, squared=True)
        metrics = dict(mse=mse, rmse=rmse)

    return model, metrics, y_pred


def tune_hyperparameters(
    model_class: Callable[..., BaseEstimator],
    X_train: csr_matrix,
    y_train: Series,
    X_val: csr_matrix,
    y_val: Series,
    callback: Optional[Callable[..., None]] = None,
    eval_metric: Callable[[Series, Series], float] = mean_squared_error,
    fit_params: Optional[Dict] = None,
    hyperparameters: Optional[Dict] = None,
    max_evaluations: int = 50,
    random_state: int = 42,
    dv = None,
    train_year: int = 2013,
    val_year: int = 2014, 
    use_dv: int = 0
) -> Dict:
    def __objective(
        params: Dict,
        X_train=X_train,
        X_val=X_val,
        callback=callback,
        eval_metric=eval_metric,
        fit_params=fit_params,
        model_class=model_class,
        dv=dv,
        y_train=y_train,
        y_val=y_val,
        use_dv = use_dv
    ) -> Dict[str, Union[float, str]]:
        mlflow.set_tracking_uri("http://mlflow:5000")
        mlflow.set_experiment("basketball")
        with mlflow.start_run():
            mlflow.set_tag("model", model_class)
            mlflow.set_tag("validation_year", val_year)
            mlflow.set_tag("train_year", train_year)
            mlflow.set_tag("use_dv", use_dv)
            mlflow.log_params(params)
            model, metrics, predictions = train_model(
                model_class(**params),
                X_train,
                y_train,
                X_val=X_val,
                y_val=y_val,
                eval_metric=eval_metric,
                fit_params=fit_params,
            )

            if callback:
                callback(
                    hyperparameters=params,
                    metrics=metrics,
                    model=model,
                    predictions=predictions,
                )

            mlflow.log_metric("rmse", metrics['rmse'])
            model_class_name=str(model_class).split('.')[-1].replace("'>",'')
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials.json'

            mlflow.sklearn.log_model(artifact_path="",sk_model=model)
            if dv is not None:
                with open(f'{model_class_name}_dv.bin', 'wb') as f_out:
                    pickle.dump(dv, f_out)
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials.json'
                mlflow.log_artifact(local_path=f"{model_class_name}_dv.bin", artifact_path="dv")


        return dict(loss=metrics['rmse'], status=STATUS_OK)

    space, choices = build_hyperparameters_space(
        model_class,
        random_state=random_state,
        **(hyperparameters or {}),
    )

    best_hyperparameters = fmin(
        fn=__objective,
        space=space,
        algo=tpe.suggest,
        max_evals=max_evaluations,
        trials=Trials(),
    )

    # Convert choice index to choice value.
    for key in HYPERPARAMETERS_WITH_CHOICE_INDEX:
        if key in best_hyperparameters and key in choices:
            idx = int(best_hyperparameters[key])
            best_hyperparameters[key] = choices[key][idx]

    # fmin will return max_depth as a float for some reason
    for key in [
        'max_depth',
        'max_iter',
        'min_samples_leaf',
    ]:
        if key in best_hyperparameters:
            best_hyperparameters[key] = int(best_hyperparameters[key])

    return best_hyperparameters
