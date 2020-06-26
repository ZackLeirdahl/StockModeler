import pandas as pd

def append_change(func):
    def wrapper(self, df):
        df = func(self, df)
        df[df.iloc[:,1].name+'_change'] = [0] + [round(df.iloc[i,1] - df.iloc[i-1,1],4) for i in range(1, df.shape[0])]
        df[df.iloc[:,1].name+'_changePercent'] = [0] + [round(100*(df.iloc[i,2] / df.iloc[i-1,1]),2) for i in range(1, df.shape[0])]
        return df.iloc[:,1:]
    return wrapper

def finish(func):
    def wrapper(self, df):
        self.df = func(self,df)
        return {'root': self.root, 'descriptor': self.descriptor, 'df': self.df}
    return wrapper

class TimeSeriesArchive:

    COLUMNS = ['implied_volatility','call_open_interest','put_open_interest','call_volume','put_volume','volume','open_interest']

    def __init__(self, *args, **kwargs):
        self.symbol, self.descriptor, self.root = args[0], 'timeseries', 'options'
        self.data = self.get_frame(args[1])
    
    @finish
    def get_frame(self, df):
        return pd.DataFrame(pd.Series(list(df['date'].unique()), name='date')).join([getattr(self, 'get_%s' % col)(df) for col in self.COLUMNS])
        
    @append_change
    def get_implied_volatility(self, df):
        return pd.DataFrame([{'date': d, 'implied_volatility': df[df['date'] == d]['implied_volatility'].mean()} for d in list(df['date'].unique())])[['date','implied_volatility']]

    @append_change
    def get_call_open_interest(self, df):
        return pd.DataFrame([{'date':d, 'call_open_interest': df[df['date'] == d]['call_open_interest'].min()} for d in list(df['date'].unique())])[['date','call_open_interest']]

    @append_change
    def get_put_open_interest(self, df):
        return pd.DataFrame([{'date':d, 'put_open_interest': df[df['date'] == d]['put_open_interest'].min()} for d in list(df['date'].unique())])[['date','put_open_interest']]

    @append_change
    def get_call_volume(self, df):
        return pd.DataFrame([{'date':d, 'call_volume': df[df['date'] == d]['call_volume'].max()} for d in list(df['date'].unique())])[['date','call_volume']]

    @append_change
    def get_put_volume(self, df):
        return pd.DataFrame([{'date':d, 'put_volume': df[df['date'] == d]['put_volume'].max()} for d in list(df['date'].unique())])[['date','put_volume']]

    @append_change
    def get_volume(self, df):
        return pd.DataFrame([{'date':d, 'volume': df[df['date'] == d]['put_volume'].max() + df[df['date'] == d]['call_volume'].max()} for d in list(df['date'].unique())])[['date','volume']]
    
    @append_change
    def get_open_interest(self, df):
        return pd.DataFrame([{'date':d, 'open_interest': df[df['date'] == d]['put_open_interest'].max() + df[df['date'] == d]['call_open_interest'].max()} for d in list(df['date'].unique())])[['date','open_interest']]
