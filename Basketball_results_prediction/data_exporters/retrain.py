from mage_ai.orchestration.triggers.api import trigger_pipeline
if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter
from mlflow.entities import ViewType
import mlflow
import requests


@data_exporter
def trigger(data, *args, **kwargs):
    train_year, val_year, use_dv, logged_model = data

    mlflow.set_tracking_uri("http://mlflow:5000")

    runs_mae = mlflow.search_runs(
    experiment_names=["Model evaluation with Evidently"],
    run_view_type=ViewType.ACTIVE_ONLY,
    max_results=100,
    filter_string=f"params.model = '{logged_model}' and metrics.current_sample>150 and metrics.significant_mae_diff=1")
    
    runs_drift = mlflow.search_runs(
    experiment_names=["Model evaluation with Evidently"],
    run_view_type=ViewType.ACTIVE_ONLY,
    max_results=100,
    #order_by=["metrics.rmse ASC"],
    filter_string=f"params.model = '{logged_model}' and metrics.current_sample>150 and metrics.total_detected>2")

    if len(runs_drift)+len(runs_mae)>0:
        if train_year<2017:
            train_year=train_year+1
            val_year=train_year+1
        r=requests.get('http://localhost:6789/api/pipelines?include_schedules=1')
        j=r.json()
        for el in j['pipelines']:
            for sh in el['schedules']:
                if sh['name']=='GLOBAL_DATA_PRODUCT_TRIGGER' and sh['schedule_type']=='api':
                    trigger_id=sh['id']
        r=requests.post(
            f'http://localhost:6789/api/pipeline_schedules/{trigger_id}/pipeline_runs/fe9b2f2228444b739bf9e191304675d7', data=str({
  "pipeline_run": {
    "variables": {
      "use_dv": 0,
      "train_year": train_year,
      "val_year": val_year
      }}}).replace("'",'"'))
        print(r.json())



        


    
    
