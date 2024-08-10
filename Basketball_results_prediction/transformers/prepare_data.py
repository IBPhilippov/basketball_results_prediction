if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

def prepare_data(val,coltype):
    if coltype=='pct':
        if val>1:
            val=val/100
    return val
def transform_data(df, *args, **kwargs):
    
    df['target'] = df.h_points-df.a_points
    df=df.fillna(0)
    for col in 'h_two_points_pct','h_three_points_pct','a_two_points_pct','a_three_points_pct':
        df[col]=df[col].map(lambda x: prepare_data(x,'pct'))
        df=df[df[col]<1]
    

    X=df[['h_two_points_pct','h_two_points_att','h_three_points_pct','h_three_points_att','h_steals','h_blocks','h_personal_fouls','a_two_points_pct','a_two_points_att','a_three_points_pct','a_three_points_att','a_steals','a_blocks','a_personal_fouls']]
    y=df.target
    return X,y

@transformer
def transform(data, *args, **kwargs):
    train_data, val_data, train_year, val_year, use_dv = data[0], data[1], data[2], data[3],  data[4]
    X_train,y_train=transform_data(train_data)
    X_val,y_val=transform_data(val_data)

    return X_train, y_train, X_val, y_val, train_year, val_year, use_dv



@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
