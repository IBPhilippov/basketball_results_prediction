import requests
from time import sleep
from flask import Flask, request, jsonify
from google.cloud import storage
import os
import json
def load_from_gcs():
    bucket_name=os.environ['ARTIFACT_STORAGE']
    storage_client = storage.Client.from_service_account_json('credentials.json')
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.get_blob('predictions/tmp.json')
    data = json.loads(blob.download_as_string())
    return data['prediction']

def get_prediction(data):
   r=requests.get('http://lmage-orc:6789/api/pipelines?include_schedules=1')
   j=r.json()
   for el in j['pipelines']:
    for sh in el['schedules']:
        if sh['name']=='basketball_predict' and sh['schedule_type']=='api':
            trigger_id=sh['id']
    r=requests.post(url=f'http://mage-orc:6789/api/pipeline_schedules/{trigger_id}/pipeline_runs/d7989ff289e04a32becd553b733fa5fc', data=data)
    print(r.json())
    status='running'
    while status not in ['completed','failed']:
        sleep(1)
        r=requests.get('http://mage-orc:6789/api/pipeline_schedules/{trigger_id}/pipeline_runs?api_key=d7989ff289e04a32becd553b733fa5fc' )
        j=r.json()
        status=j['pipeline_runs'][0]['status']
    output=load_from_gcs()
    return output


app = Flask('app')

@app.route('/predict', methods=['POST'])
def predict_endpoint():
    event = request.get_json()
    event =   {"pipeline_run": { "variables": { "event_data": event }}}

    event = str(event).replace("'",'"')
    pred = get_prediction(event)

    result = {
        'results': pred}

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=9696)