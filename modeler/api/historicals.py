import pandas as pd
from datetime import date, datetime
from dateutil.parser import parse
try:
    from iex.base import IEXClient
    from util import get_last_week_dates, is_date, find_range
except:
    from .iex.base import IEXClient
    from .util import get_last_week_dates, is_date, find_range

##################################### WRAPPERS ##################################################
def clean_frame(func):
    def wrapper(self, **kwargs):
        df = func(self, **kwargs)[self.fields['minute' if self.interval != 'daily' else 'daily']].dropna()
        for i, r in df[df['open'].isna()].iterrows():
            df.loc[i] = [r['date'],r['minute'],df.iloc[i-1,2],df.iloc[i-1,3],df.iloc[i-1,4],df.iloc[i-1,5],0]#{'date':r['date'],'minute':r['minute'],'open':df.iloc[i-1,2],'high':df.iloc[i-1,3],'low':df.iloc[i-1,4],'close':df.iloc[i-1,5],'volume':0}
        if kwargs.get('interval') in ['dynamic','minute']:
            df['volume'] = df['volume'].apply(lambda x: x *100)
        if self.interval != 'daily':
            df['change'] = [0] + [df.iloc[i,5] - df.iloc[i-1,5] for i in range(1, df.shape[0])]
            df['changePercent'] = [0] + [round(100*(df.iloc[i,7] / df.iloc[i-1,5]),2) for i in range(1, df.shape[0])]
            #df['change'] = [0] + [df.loc[i,'close'] - df.loc[i-1,'close'] for i in range(1, df.shape[0])]
            #df['changePercent'] = [0] + [round(100*(df.loc[i,'change'] / df.loc[i-1,'close']),2) for i in range(1, df.shape[0])]
        self.df = df
        return {'root': self.root, 'descriptor': self.interval, 'df': self.df}
    return wrapper

class Historicals(IEXClient):
    """
    Parameters
    ----------
    symbol : str
        the symbol of the stock
    interval : str, optional
        if 'minute', will return the specific dates' data with 1 minute interval,
        if 30, will return the last month's trading data in 30 minute intervals
        if not included, will return OHLCV for the specific date
    new : bool, optional
        if True, will write a new frame
    range : str, optional
        if 'backfill', frame will be read from a file and have all the trading days between the last record and the current date appended
        if 'dynamic', frame will be today's trading data in 1 minute intervals
        if valid date string, see 'interval' parameter
    input : str, DataFrame, optional
        the full path to an options frame or a loaded frame.
    """
    def __init__(self, *args, **kwargs):
        IEXClient.__init__(self, symbol=args[0].upper())
        self.df, self.interval, self.root = kwargs.get('input'), str(kwargs.get('interval','daily')), 'historicals'
        self.data = self.get_frame(**kwargs)
           
    @clean_frame
    def get_frame(self, **kwargs):
        if self.interval == 'dynamic':
            return pd.DataFrame(self.get_historical_prices(range='dynamic',includeToday=False).to_dict()['data']).transpose()
        if kwargs.get('new',False):
            return self.get_historical_prices(range='5y',includeToday=False) if self.interval == 'daily' else (pd.concat([self.get_historical_prices(range='date', exactDate=d, chartByDay=False) for d in get_last_week_dates()]) if self.interval == 'minute' else (self.get_historical_prices(range='1mm',includeToday=False) if self.interval == '30' else self.get_historical_prices(range='5dm',includeToday=False)))
        if is_date(kwargs.get('range')) and kwargs.get('interval') == 'minute':
            return pd.DataFrame(self.get_historical_prices(range='date', exactDate=kwargs['range'], chartByDay=False))
        if kwargs.get('range') == 'backfill' and kwargs.get('interval') == 'minute':
            return self.df.append(pd.concat([self.get_historical_prices(range='date', exactDate=d, chartByDay=False) for d in get_last_week_dates(str(df.loc[len(df.index)-1,'date']))]))
        if kwargs.get('range') == 'backfill':
            return self.df.append(pd.Series(self.get_previous_day_prices()),ignore_index=True) if (parse(str(df.loc[len(df.index)-1,'date'])).toordinal() -1 == datetime.now().toordinal()) or (parse(str(df.loc[len(df.index)-1,'date'])).weekday() == 4 and datetime.now().weekday() == 0 and datetime.now().toordinal() - parse(str(df.loc[len(df.index)-1,'date'])).toordinal() == 3) else self.df.append(pd.DataFrame([v for k, v in {d['date']: d for d in self.get_historical_prices(range=find_range(df.loc[len(df.index)-1,'date']), includeToday=False)}.items() if parse(k, fuzzy=False).toordinal() > parse((str(df.loc[len(df.index)-1,'date'])).strftime('%Y%m%d'),fuzzy=False).toordinal()]))
        return self.df
