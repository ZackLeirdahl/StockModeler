import pandas as pd
from dateutil.parser import parse
from datetime import date, datetime
from .robinhood.chain import Chain

##################################### WRAPPERS ##################################################
def clean_frame(func):
    def wrapper(self, **kwargs):
        df = func(self, **kwargs)
        if kwargs.get('dummy'):
            df['volume'] = df['volume'].apply(lambda x: 0)
        self.df = df[~df['expiration_date'].isin([exp for exp in df['expiration_date'].unique() if parse(exp) < datetime.today()])]
        return {'root': self.root, 'descriptor': self.interval, 'df': self.df}
    return wrapper
        
class ChainMeasurements(Chain):
    """
    A class that containing the methods and attributes to fetch and apply different option calculations to a stock.
    Parameters
    ----------
    symbol : str
        the symbol to perform option analysis on
    interval : str, optional
        the interval of the options measurements file (if measurements_from_file is True), possible values are 'dynamic','daily' (default is 'dynamic')
    input : str, DataFrame, optional
        the full path to an options frame or a loaded frame.
    dummy : bool, optional
        if True, will blank out volume for a cumulative summary (default is false)
    """

    FIELDS = ['id','expiration_date','type','strike_price','implied_volatility','open_interest','volume','time_stamp']

    def __init__(self, *args, **kwargs):
        Chain.__init__(self, args[0])
        self.df, self.interval, self.root = kwargs.get('input'), kwargs.get('interval','dynamic'), 'options'
        self.data = self.get_frame(dummy=kwargs.get('dummy',False))

    @clean_frame
    def get_frame(self, **kwargs):
        return self.df.append(self.options[self.FIELDS]) if self.df is not None else self.options[self.FIELDS]