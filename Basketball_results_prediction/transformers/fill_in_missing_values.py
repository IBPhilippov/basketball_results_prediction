if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test
import pandas as pd
import evidently

@custom
def transform_custom(data, *args, **kwargs):
    #data = kwargs.get('data')
    data2 = {'features': {'h_three_points_pct': {'0': 0.10800000000000001, '1': 0.348}, 'h_three_points_att': {'0': 99.0, '1': 23.0}, 'h_two_points_pct': {'0': 0.41, '1': 0.41}, 'h_two_points_att': {'0': 39.0, '1': 39.0}, 'h_offensive_rebounds': {'0': 5.0, '1': 5.0}, 'h_defensive_rebounds': {'0': 30.0, '1': 30.0}, 'h_turnovers': {'0': 9.0, '1': 9.0}, 'h_steals': {'0': 0.0, '1': 0.0}, 'h_blocks': {'0': 4.0, '1': 4.0}, 'h_personal_fouls': {'0': 15.0, '1': 15.0}, 'h_points': {'0': 70.0, '1': 70.0}, 'a_three_points_pct': {'0': 0.41700000000000004, '1': 0.41700000000000004}, 'a_three_points_att': {'0': 12.0, '1': 12.0}, 'a_two_points_pct': {'0': 0.46299999999999997, '1': 0.46299999999999997}, 'a_two_points_att': {'0': 54.0, '1': 54.0}, 'a_offensive_rebounds': {'0': 5.0, '1': 5.0}, 'a_defensive_rebounds': {'0': 27.0, '1': 27.0}, 'a_turnovers': {'0': 10.0, '1': 10.0}, 'a_steals': {'0': 2.0, '1': 2.0}, 'a_blocks': {'0': 5.0, '1': 5.0}, 'a_personal_fouls': {'0': 17.0, '1': 17.0}, 'a_points': {'0': 73.0, '1': 73.0}}, 'logged_model': 'gs://ibphilippov-mlops-storage/artifacts/719fb9ce3cf143408d7e63298521794e/artifacts/', 'prediction': [8.340391221695402, 9.876255483351072]}
    event_data = pd.DataFrame.from_dict(data2['features'])
    event_data = event_data[['h_two_points_pct','h_two_points_att','h_three_points_pct','h_three_points_att','h_steals','h_blocks','h_personal_fouls','h_points','a_two_points_pct','a_two_points_att','a_three_points_pct','a_three_points_att','a_steals','a_blocks','a_personal_fouls','a_points']]
    if type(data['prediction'])==dict:
        event_pred = pd.DataFrame([data['prediction']],columns=['prediction'])
    else:
        event_pred = pd.DataFrame(data['prediction'],columns=['prediction'])
    for i in range(len(data['prediction'])):
        event_data.loc[i,'prediction']=data['prediction'][i]
    if 'h_points' in event_data.columns and 'a_points' in event_data.columns:
        event_data['target']=event_data['h_points']-event_data['a_points']
        event_data = event_data.drop(columns=['h_points','a_points'])
    logged_model=data['logged_model']
    return event_data, logged_model




@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
