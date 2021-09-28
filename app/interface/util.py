from datetime import datetime

def convert_timestamp(df, **kwargs):
    df['time_stamp'] = df['time_stamp'].apply(lambda x: datetime.fromtimestamp(x))
    return df[df['time_stamp'] == list(df['time_stamp'].unique())[-1]] if kwargs.get('last_time_stamp', True) else df

def filter_measurements(df, **kwargs):
    for k, v in kwargs.items():
        df = df[df[k] == v]
    return df