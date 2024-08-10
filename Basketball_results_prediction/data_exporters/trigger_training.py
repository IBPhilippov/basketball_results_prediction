if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter
import requests


@data_exporter
def trigger(*args, **kwargs):
    requests.post('http://localhost:6789/api/pipeline_schedules/4/pipeline_runs/73dd5fc8d6c84d9aa9d714fa408b2850')