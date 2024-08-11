if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test
import mlflow
from mlflow import MlflowClient
import os


@transformer
def transform(data, data_2, *args, **kwargs):
    X_train, X_val, y_train, y_val, dv, train_year, val_year, use_dv = data_2['build']
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials.json'
    model = mlflow.pyfunc.load_model(data[1])
    X_train['prediction']= model.predict(X_train)
    X_train['target']=y_train
    return X_train, train_year, val_year, use_dv


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'