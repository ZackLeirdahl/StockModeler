from datetime import datetime
import pandas as pd
import mpld3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
from firebase import Firebase

def convert_timestamp(df, **kwargs):
    df['time_stamp'] = df['time_stamp'].apply(lambda x: datetime.fromtimestamp(x))
    return df[df['time_stamp'] == list(df['time_stamp'].unique())[-1]] if kwargs.get('last_time_stamp', True) else df

def filter_measurements(df, **kwargs):
    for k, v in kwargs.items():
        df = df[df[k] == v]
    return df

def append_changes(func):
    def wrapper(self, df, **kwargs):
        df = func(self, df, **kwargs)
        for m in ['volume','open_interest','implied_volatility']:
            df[m + '_change'] = df[m].diff()
            df[m + '_change_pct'] =  [0] + [round(100*(df.iloc[i,3 if m=='volume' else (5 if m == 'open_interest' else 7)] / df.iloc[i-1,0 if m=='volume' else (1 if m=='open_interest' else 2)]),2) for i in range(1,df.shape[0])]
        return df.reset_index()
    return wrapper

def plot(func):
    def wrapper(self):

        #fig = plt.figure(figsize = (18,8))
        df = func(self)
        fig, ax = plt.subplots(figsize = (9,4))
        ax.plot(df[self.index], df[self.lines])
        ax.set(xlabel='time (s)', ylabel='voltage (mV)',title='About as simple as it gets, folks')
        ax.grid()
        #plt.plot(df[self.index], df[self.lines])
        #print(mpld3.fig_to_dict(fig))
        plt.show()
        return None
    return wrapper

class Plotter:
    def __init__(self, symbol, descriptor, **kwargs):
        self.df = self.get_time_series(Firebase().get('options/{}_options_{}.csv'.format(symbol, descriptor)))
        self.num_rows = self.df.shape[0] if not kwargs.get('num_rows') else kwargs['num_rows']
        self.lines = list(self.df.columns)[1:] if not kwargs.get('lines') else kwargs['lines']
        self.index = list(self.df.columns)[0] if not kwargs.get('index') else kwargs['index']
        self.kind = 'line' if not kwargs.get('kind') else kwargs['kind']
        self.linestyle = 'solid' if not kwargs.get('linestyle') else kwargs['linestyle']
        self.stacked = False if not kwargs.get('stacked') else kwargs['stacked']
        self.subplots = False if not kwargs.get('subplots') else kwargs['subplots']
        self.shape_data()
    
    @plot
    def shape_data(self):
        df = self.df.head(self.num_rows)[[self.index]+self.lines]
        df.index = df[self.index].astype('datetime64') if self.kind == 'line' and self.index == 'date' else df[self.index]
        return df

    @append_changes
    def get_time_series(self, df, **kwargs):
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
        return pd.concat([df[['time_stamp','volume','open_interest']].groupby(['time_stamp']).sum(),df[(df['volume'] > 0) & (df['implied_volatility'] > 0)][['time_stamp', 'implied_volatility']].groupby(['time_stamp']).mean()['implied_volatility']],axis=1)

Plotter('AMD','dynamic', kind='line',linestyle='dotted',lines = ['implied_volatility'])