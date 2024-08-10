if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter
from sklearn.feature_extraction import DictVectorizer


@data_exporter
def export_data(data, *args, **kwargs):
    X_train, y_train, X_val, y_val, train_year, val_year, use_dv = data[0], data[1], data[2], data[3], data[4], data[5], data[6]
    if use_dv==1:
        dv = DictVectorizer()
        train_dicts = X_train.to_dict(orient='records')
        X_train = dv.fit_transform(train_dicts)
    else:
        dv = None
    #train_year = kwargs['train_year'] 
    #val_year = kwargs['val_year']


    if X_val is not None and use_dv==1:
        val_dicts = X_val.to_dict(orient='records')
        X_val = dv.transform(val_dicts)

    return  X_train, X_val, y_train, y_val, dv, train_year, val_year, use_dv
    # Specify your data exporting logic here


