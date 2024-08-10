if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter
import requests


@data_exporter
def export_data(data, *args, **kwargs)->List:
    """
    Exports data to some source.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Output (optional):
        Optionally return any object and it'll be logged and
        displayed when inspecting the block run.
    """
    r=requests.post(url='http://localhost:6789/api/pipeline_schedules/3/pipeline_runs/96a3147e2ac749929eadac81c581d8e3', data=data)

    return data

