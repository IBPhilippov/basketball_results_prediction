import os
import json
import mlflow
import base64
import pandas as pd
from cloudevents.http import CloudEvent
import functions_framework
from google.cloud import pubsub_v1
from google.cloud import storage



def prepare_data(val,coltype):
    if coltype=='pct':
        if val>1:
            val=val/100
    return val
def transform_data(df, *args, **kwargs):
    df=df.fillna(0)
    for col in 'h_two_points_pct','h_three_points_pct','a_two_points_pct','a_three_points_pct':
        df[col]=df[col].map(lambda x: prepare_data(x,'pct'))
    return df

def send_result_to_pubsub(res,project_id):

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, 'predictions-output')

    data = json.dumps(res).encode("utf-8")
    future = publisher.publish(topic_path, data)
    print(f'published message id {future.result()}')

def save_to_gcs(data,bucket_name):
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob('predictions/tmp.json')
    with blob.open(mode='w') as f:
        json.dump(data,f)


# Triggered from a message on a Cloud Pub/Sub topic.
@functions_framework.cloud_event
def predictFromPubSub(cloud_event: CloudEvent) -> None:

    data=json.loads(base64.b64decode(cloud_event.data["message"]["data"]).decode())
    if type(data['event'])==dict:
        event_data = pd.DataFrame([data['event']])
    else:
        event_data = pd.DataFrame(data['event'])
    logged_model = data['logged_model']
    project_id = data['project_id']
    bucket_name = data['bucket_name']
    model = mlflow.pyfunc.load_model(logged_model)
    df = transform_data(event_data)
    features = df[['h_two_points_pct','h_two_points_att','h_three_points_pct','h_three_points_att','h_steals','h_blocks','h_personal_fouls','a_two_points_pct','a_two_points_att','a_three_points_pct','a_three_points_att','a_steals','a_blocks','a_personal_fouls']]
    pred = model.predict(features)
    pred = pred.tolist()
    send_result_to_pubsub({'data':data['event'],'prediction':pred,'prepared_X': df.to_dict('records')}, project_id)
    save_to_gcs({'data':data['event'],'prediction':pred},bucket_name)
    return float(pred[0])
