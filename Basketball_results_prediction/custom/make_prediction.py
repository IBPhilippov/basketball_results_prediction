if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


from mage_ai.settings.repo import get_repo_path
from mage_ai.io.config import ConfigFileLoader
import json
if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test
from concurrent import futures
from google.cloud import pubsub_v1
from typing import Callable
import os
from os import path
from concurrent.futures import TimeoutError
from mlflow import MlflowClient
from google.oauth2 import service_account


def get_callback(
    publish_future: pubsub_v1.publisher.futures.Future, data: str
) -> Callable[[pubsub_v1.publisher.futures.Future], None]:
    def callback(publish_future: pubsub_v1.publisher.futures.Future) -> None:
        try:
            # Wait 60 seconds for the publish call to succeed.
            print(publish_future.result(timeout=60))
        except futures.TimeoutError:
            print(f"Publishing {data} timed out.")

    return callback

def callback_listen(message: pubsub_v1.subscriber.message.Message) -> None:
    global processed_data
    print(f"Received {message}.")
    processed_data.append(json.loads(message.data.decode('utf-8')))
    message.ack()
    return processed_data

def listen(message_sent):
    global processed_data
    project_id=os.environ['GCP_PROJECT_NAME']
    timeout = 15

    subscriber = pubsub_v1.SubscriberClient(credentials=service_account.Credentials.from_service_account_file(
        'credentials.json'))
    subscription_path = subscriber.subscription_path(project_id, 'read')
    processed_data=[]
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback_listen)
    print(f"Listening for messages on {subscription_path}..\n")

    # Wrap subscriber in a 'with' block to automatically call close() when done.
    with subscriber:
        try:
            streaming_pull_future.result(timeout=timeout)
        except TimeoutError:
            streaming_pull_future.cancel()  # Trigger the shutdown.
            streaming_pull_future.result() 
    for message in processed_data:
        if 1==1:#message['data']==message_sent['event']:
            return message['prediction'], message['prepared_X']

def publish(data):
    project_id=os.environ['GCP_PROJECT_NAME']
    topic_id = "predictions-input"
    publisher = pubsub_v1.PublisherClient(credentials=service_account.Credentials.from_service_account_file(
        'credentials.json'))
    topic_path = publisher.topic_path(project_id, topic_id)
    publish_futures = []
    data = json.dumps(data).encode('utf-8')
    publish_future = publisher.publish(topic_path, data)
    # Non-blocking. Publish failures are handled in the callback function.
    publish_future.add_done_callback(get_callback(publish_future, data))
    publish_futures.append(publish_future)

    # Wait for all the publish futures to resolve before exiting.
    futures.wait(publish_futures, return_when=futures.ALL_COMPLETED)

    print(f"Published messages with error handler to {topic_path}.")


@custom
def get_prediction(*args, **kwargs):
    """
    Template for loading data from a BigQuery warehouse.
    Specify your configuration settings in 'io_config.yaml'.

    Docs: https://docs.mage.ai/design/data-loading#bigquery
    """

    project_id=os.environ['GCP_PROJECT_NAME']
    bucket_name=os.environ['ARTIFACT_STORAGE']

    event_data = kwargs.get('event_data')
    if event_data is None:
        event_data =  [{"h_three_points_pct": 10.8, "h_three_points_att": 99.0, "h_two_points_pct": 41.0, "h_two_points_att": 39.0, "h_offensive_rebounds": 5.0, "h_defensive_rebounds": 30.0, "h_turnovers": 9.0, "h_steals": 0.0, "h_blocks": 4.0, "h_personal_fouls": 15.0, "h_points": 70.0, "a_three_points_pct": 41.7, "a_three_points_att": 12.0, "a_two_points_pct": 46.3, "a_two_points_att": 54.0, "a_offensive_rebounds": 5.0, "a_defensive_rebounds": 27.0, "a_turnovers": 10.0, "a_steals": 2.0, "a_blocks": 5.0, "a_personal_fouls": 17.0, "a_points": 73.0},{"h_three_points_pct": 34.8, "h_three_points_att": 23.0, "h_two_points_pct": 41.0, "h_two_points_att": 39.0, "h_offensive_rebounds": 5.0, "h_defensive_rebounds": 30.0, "h_turnovers": 9.0, "h_steals": 0.0, "h_blocks": 4.0, "h_personal_fouls": 15.0, "h_points": 70.0, "a_three_points_pct": 41.7, "a_three_points_att": 12.0, "a_two_points_pct": 46.3, "a_two_points_att": 54.0, "a_offensive_rebounds": 5.0, "a_defensive_rebounds": 27.0, "a_turnovers": 10.0, "a_steals": 2.0, "a_blocks": 5.0, "a_personal_fouls": 17.0, "a_points": 73.0}]
    if type(event_data)==str:
        event_data = json.loads(event_data)
    

    client = MlflowClient(tracking_uri="http://mlflow:5000")
    model_name = "basketball_predictor"
    latest_versions = client.get_latest_versions(name=model_name)

    for version in latest_versions:
        logged_model=version.source[:-5]
    print(logged_model)

    message={"event":event_data,"logged_model":logged_model,"project_id": project_id,"bucket_name": bucket_name}
    publish(message)
    prediction,features=listen(message)
    print(prediction)
    print({"features":features, "logged_model":logged_model, "prediction": prediction })
    return {"features":features, "logged_model":logged_model, "prediction": prediction }


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
