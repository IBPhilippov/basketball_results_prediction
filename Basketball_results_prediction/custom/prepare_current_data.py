if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test
import pandas as pd
import evidently

@custom
def transform_custom(*args, **kwargs):
    data = kwargs.get('sent_data')
    #data = {'features': [{'h_three_points_pct': 0.10800000000000001, 'h_three_points_att': 99.0, 'h_two_points_pct': 0.41, 'h_two_points_att': 39.0, 'h_offensive_rebounds': 5.0, 'h_defensive_rebounds': 30.0, 'h_turnovers': 9.0, 'h_steals': 0.0, 'h_blocks': 4.0, 'h_personal_fouls': 15.0, 'h_points': 70.0, 'a_three_points_pct': 0.41700000000000004, 'a_three_points_att': 12.0, 'a_two_points_pct': 0.46299999999999997, 'a_two_points_att': 54.0, 'a_offensive_rebounds': 5.0, 'a_defensive_rebounds': 27.0, 'a_turnovers': 10.0, 'a_steals': 2.0, 'a_blocks': 5.0, 'a_personal_fouls': 17.0, 'a_points': 73.0}, {'h_three_points_pct': 0.348, 'h_three_points_att': 23.0, 'h_two_points_pct': 0.41, 'h_two_points_att': 39.0, 'h_offensive_rebounds': 5.0, 'h_defensive_rebounds': 30.0, 'h_turnovers': 9.0, 'h_steals': 0.0, 'h_blocks': 4.0, 'h_personal_fouls': 15.0, 'h_points': 70.0, 'a_three_points_pct': 0.41700000000000004, 'a_three_points_att': 12.0, 'a_two_points_pct': 0.46299999999999997, 'a_two_points_att': 54.0, 'a_offensive_rebounds': 5.0, 'a_defensive_rebounds': 27.0, 'a_turnovers': 10.0, 'a_steals': 2.0, 'a_blocks': 5.0, 'a_personal_fouls': 17.0, 'a_points': 73.0}], 'logged_model': 'gs://ibphilippov-mlops-storage/artifacts/719fb9ce3cf143408d7e63298521794e/artifacts/', 'prediction': [8.340391221695402, 9.876255483351072]}
    #data={'features': [{'h_three_points_pct': 0.10800000000000001, 'h_three_points_att': 99.0, 'h_two_points_pct': 0.41, 'h_two_points_att': 39.0, 'h_offensive_rebounds': 5.0, 'h_defensive_rebounds': 30.0, 'h_turnovers': 9.0, 'h_steals': 0.0, 'h_blocks': 4.0, 'h_personal_fouls': 15.0, 'h_points': 70.0, 'a_three_points_pct': 0.41700000000000004, 'a_three_points_att': 12.0, 'a_two_points_pct': 0.46299999999999997, 'a_two_points_att': 54.0, 'a_offensive_rebounds': 5.0, 'a_defensive_rebounds': 27.0, 'a_turnovers': 10.0, 'a_steals': 2.0, 'a_blocks': 5.0, 'a_personal_fouls': 17.0, 'a_points': 73.0}, {'h_three_points_pct': 0.348, 'h_three_points_att': 23.0, 'h_two_points_pct': 0.41, 'h_two_points_att': 39.0, 'h_offensive_rebounds': 5.0, 'h_defensive_rebounds': 30.0, 'h_turnovers': 9.0, 'h_steals': 0.0, 'h_blocks': 4.0, 'h_personal_fouls': 15.0, 'h_points': 70.0, 'a_three_points_pct': 0.41700000000000004, 'a_three_points_att': 12.0, 'a_two_points_pct': 0.46299999999999997, 'a_two_points_att': 54.0, 'a_offensive_rebounds': 5.0, 'a_defensive_rebounds': 27.0, 'a_turnovers': 10.0, 'a_steals': 2.0, 'a_blocks': 5.0, 'a_personal_fouls': 17.0, 'a_points': 73.0}], 'logged_model': 'gs://test-mlops-philippov/1/53d01f5426f947018e1df9fc533d6f31/artifacts/', 'prediction': [-3.592974506799493, 5.767526498804508]}
    event_data = pd.DataFrame.from_records(data['features'])
    event_data = event_data[['h_two_points_pct','h_two_points_att','h_three_points_pct','h_three_points_att','h_steals','h_blocks','h_personal_fouls','h_points','a_two_points_pct','a_two_points_att','a_three_points_pct','a_three_points_att','a_steals','a_blocks','a_personal_fouls','a_points']]
    if type(data['prediction'])==dict:
        event_pred = pd.DataFrame([data['prediction']],columns=['prediction'])
    else:
        event_pred = pd.DataFrame(data['prediction'],columns=['prediction'])
    event_data=event_data.join(event_pred)
    if 'h_points' in event_data.columns and 'a_points' in event_data.columns:
        event_data['target']=event_data['h_points']-event_data['a_points']
        event_data = event_data.drop(columns=['h_points','a_points'])
    logged_model=data['logged_model']
    return [event_data, logged_model]




@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
