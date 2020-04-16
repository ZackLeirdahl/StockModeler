import pandas as pd
from datetime import datetime
from firebase import Firebase

def convert_timestamp(df, **kwargs):
    df['time_stamp'] = df['time_stamp'].apply(lambda x: datetime.fromtimestamp(x))
    return df[df['time_stamp'] == list(df['time_stamp'].unique())[-1]] if kwargs.get('last_time_stamp', True) else df

def filter_measurements(df, **kwargs):
    for k, v in kwargs.items():
        df = df[df[k] == v]
    return df

def append_changes(func):
    def wrapper(self, **kwargs):
        df = func(self, **kwargs)
        for m in ['volume','open_interest','implied_volatility']:
            df[m + '_change'] = df[m].diff()
            df[m + '_change_pct'] =  [0] + [round(100*(df.iloc[i,3 if m=='volume' else (5 if m == 'open_interest' else 7)] / df.iloc[i-1,0 if m=='volume' else (1 if m=='open_interest' else 2)]),2) for i in range(1,df.shape[0])]
        return df
    return wrapper

@append_changes
def time_series_summary(df, **kwargs):
    """A method to get the summary of changes in options measurements
    Parameters
    ----------
    type : str, optional
        the option type
    expiration_date : str, optional
        the expiration of the option, fmt = YYYY-MM-DD
    strike_price : int/float, optional
        the strike_price
    Returns
    -------
    pd.DataFrame
        a DataFrame of the summary data
    """
    df = convert_timestamp(filter_measurements(df,**kwargs), last_time_stamp = False)
    return pd.concat([df[['time_stamp','volume','open_interest']].groupby(['time_stamp']).sum(),df[['time_stamp', 'implied_volatility']].groupby(['time_stamp']).mean()['implied_volatility']],axis=1)

def option_summary(df, **kwargs):
    """A method to get the summary of changes in options measurements
    Parameters
    ----------
    type : str, optional
        the option type
    expiration_date : str, optional
        the expiration of the option, fmt = YYYY-MM-DD
    strike_price : int/float, optional
        the strike_price
    Returns
    -------
    pd.DataFrame
        a DataFrame of the summary data
    """
    df = convert_timestamp(filter_measurements(df,**kwargs), last_time_stamp = True)
    return {**df[['volume','open_interest']].sum().to_dict(), **df[['implied_volatility']].mean().to_dict()}

def option_spread(df):
    data = option_summary(df)
    results = df.groupby(['type'])[['volume','open_interest']].sum().to_dict()
    return pd.DataFrame([{**{'_'.join([m, t]) : 100* round(results[m][t] / data[m],2) for m in ['volume', 'open_interest'] for t in ['call', 'put']}, **data}])

df = Firebase().get('options/SPY_options_daily.csv')
print(option_spread(df))