if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test
import evidently
import mlflow
import pandas as pd
from evidently.pipeline.column_mapping import ColumnMapping
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, RegressionPreset
import numpy as np
def eval_drift(reference, production, column_mapping):

    data_drift_report = Report(metrics=[DataDriftPreset()])
    data_drift_report.run(reference_data=reference, current_data=production, column_mapping=column_mapping)
    report = data_drift_report.as_dict()
    drifts = []
    for feature in column_mapping.numerical_features:
        drifts.append((feature, report["metrics"][1]["result"]["drift_by_columns"][feature]["drift_score"]))
    drifts.append(('total_detected',sum([int(report["metrics"][1]["result"]["drift_by_columns"][feature]["drift_detected"]) for feature in column_mapping.numerical_features])))
    return drifts

def eval_regression(reference, production, column_mapping):

    regression_report = Report(metrics=[RegressionPreset()])
    regression_report.run(reference_data=reference, current_data=production, column_mapping=column_mapping)
    report = regression_report.as_dict()
    mae_diff = (report["metrics"][0]['result']['current']['mean_abs_error']-report["metrics"][0]['result']['current']['abs_error_std']*1.96)-(report["metrics"][0]['result']['reference']['mean_abs_error']+report["metrics"][0]['result']['reference']['abs_error_std']*1.96)
    return mae_diff

@transformer
def transform(data, data_2, *args, **kwargs):

    data, logged_model = data[0], data[1]
    reference, train_year, val_year, use_dv = data_2
    reference = reference.astype(np.float64)
    data_columns = ColumnMapping()
    data_columns.numerical_features = ['h_two_points_pct','h_two_points_att','h_three_points_pct','h_three_points_att','h_steals','h_blocks','h_personal_fouls','a_two_points_pct','a_two_points_att','a_three_points_pct','a_three_points_att','a_steals','a_blocks','a_personal_fouls']
    data_columns.target = 'target'
    data_columns.prediction = 'prediction'
        
    #log into MLflow
    mlflow.set_tracking_uri("http://mlflow:5000")
    mlflow.set_experiment('Model evaluation with Evidently')

    #start new run
    with mlflow.start_run() as run: 
        
        mlflow.log_param("model", logged_model)

        # Log metrics
        metrics = eval_drift(reference[['h_two_points_pct','h_two_points_att','h_three_points_pct','h_three_points_att','h_steals','h_blocks','h_personal_fouls','a_two_points_pct','a_two_points_att','a_three_points_pct','a_three_points_att','a_steals','a_blocks','a_personal_fouls']], 
                            data[['h_two_points_pct','h_two_points_att','h_three_points_pct','h_three_points_att','h_steals','h_blocks','h_personal_fouls','a_two_points_pct','a_two_points_att','a_three_points_pct','a_three_points_att','a_steals','a_blocks','a_personal_fouls']], 
                            column_mapping=data_columns)
        for feature in metrics:
            mlflow.log_metric(feature[0], round(feature[1], 3))
        
        if 'target' in data.columns:
            mae_diff = eval_regression(reference, 
                            data, 
                            column_mapping=data_columns)
            
            mlflow.log_metric('mae_diff', round(mae_diff, 3))
            mlflow.log_metric('significant_mae_diff', mae_diff>0)
            mlflow.log_metric('current_sample', len(data))



        
    return train_year, val_year, use_dv, logged_model


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'