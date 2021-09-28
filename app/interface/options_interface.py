import pandas as pd
from .util import convert_timestamp, filter_measurements
from .wrappers import append_changes, plot
from .firebase_interface import get
from ..api.robinhood import Chain

class OptionsData:

    ENDPOINTS = ['active_options','average_implied_volatility','options_spread','max_pain','price']

    def __init__(self, symbol):
        self.chain = Chain(symbol)
        self.data = None if not isinstance(self.chain.options,pd.DataFrame) else self.get_data()

    def get_data(self):
        return {ep: getattr(self,'get_%s' % ep)() for ep in self.ENDPOINTS}
    
    def get_active_options(self, limit=10):
        return self.chain.get_active_options(limit=limit).to_dict('records') + self.chain.get_active_options(limit=limit, option_type='put').to_dict('records')

    def get_options_spread(self):
        return self.chain.get_option_spread().to_dict('records')[0]
    
    def get_max_pain(self):
        mp = str(self.chain.get_max_pain().iloc[0,0])
        return mp.split('.')[0] if mp.split('.')[1][0] == '0' else mp.split('.')[0] + '.' + mp.split('.')[1][0]
    
    def get_average_implied_volatility(self):
        return self.chain.get_average_implied_volatility()

    def get_price(self):
        return self.chain.price


class OptionsTimeSeries:
    def __init__(self, symbol, descriptor, **kwargs):
        self.symbol = symbol
        self.df = self.get_time_series(get('options/{}_options_{}.csv'.format(symbol, descriptor)))
        if type(self.df) != bool:
            self.num_rows = self.df.shape[0] if not kwargs.get('num_rows') else kwargs['num_rows']
            self.lines = list(self.df.columns)[1:] if not kwargs.get('lines') else kwargs['lines']
            self.index = list(self.df.columns)[0] if not kwargs.get('index') else kwargs['index']
            self.kind = 'line' if not kwargs.get('kind') else kwargs['kind']
            self.linestyle = 'solid' if not kwargs.get('linestyle') else kwargs['linestyle']
            self.stacked = False if not kwargs.get('stacked') else kwargs['stacked']
            self.subplots = False if not kwargs.get('subplots') else kwargs['subplots']
        self.fig = self.shape_data() if type(self.df) != bool else None
    
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
        if type(df) == bool:
            return False
        df = convert_timestamp(filter_measurements(df,**kwargs), last_time_stamp = False)
        return pd.concat([df[['time_stamp','volume','open_interest']].groupby(['time_stamp']).sum(),df[(df['volume'] > 0) & (df['implied_volatility'] > 0)][['time_stamp', 'implied_volatility']].groupby(['time_stamp']).mean()['implied_volatility']],axis=1)