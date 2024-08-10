if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test
from mlflow.entities import ViewType
from mlflow import MlflowClient
import mlflow
@transformer
def transform(data, *args, **kwargs):
    print(data)
    train_year=data[0]
    print(train_year)
    mlflow.set_tracking_uri("http://mlflow:5000")
    mlflow.set_experiment("basketball")
    runs = mlflow.search_runs(
        experiment_names=["basketball"],
        run_view_type=ViewType.ACTIVE_ONLY,
        max_results=1,
        order_by=["metrics.rmse ASC"],
        filter_string=f'tags.train_year="{train_year}"')
    run_id = runs.loc[0,'run_id']
    print(run_id)

    model_uri = f"runs:/{run_id}/model"

    mlflow.register_model(model_uri=model_uri, name="basketball_predictor")

    return 1


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'