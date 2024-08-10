if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter
import requests


@data_exporter
def export_data(data, *args, **kwargs):
    """
    Exports data to some source.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Output (optional):
        Optionally return any object and it'll be logged and
        displayed when inspecting the block run.
    """
    r=requests.get('http://localhost:6789/api/pipelines?include_schedules=1')
    j=r.json()
    for el in j['pipelines']:
        for sh in el['schedules']:
            if sh['name']=='add_to_monitoring' and sh['schedule_type']=='api':
                trigger_id=sh['id']
    r=requests.post(url=f'http://localhost:6789/api/pipeline_schedules/{trigger_id}/pipeline_runs/96a3147e2ac749929eadac81c581d8e3', data=str(data).replace("'",'"'))
    print(r.json())
    return data

