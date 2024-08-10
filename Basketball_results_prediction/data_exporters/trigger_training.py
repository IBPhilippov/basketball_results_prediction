if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter
import requests


@data_exporter
def trigger(*args, **kwargs):
    r=requests.get('http://localhost:6789/api/pipelines?include_schedules=1')
    j=r.json()
    for el in j['pipelines']:
        for sh in el['schedules']:
            if sh['name']=='trigger_training' and sh['schedule_type']=='api':
                trigger_id=sh['id']
    requests.post(f'http://localhost:6789/api/pipeline_schedules/{trigger_id}/pipeline_runs/73dd5fc8d6c84d9aa9d714fa408b2850')