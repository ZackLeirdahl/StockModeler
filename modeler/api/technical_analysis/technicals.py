import pandas as pd
try:
    from indicators import Indicators
    from overlays import Overlays
    from util import *
except:
    from .indicators import Indicators
    from .overlays import Overlays
    from .util import *

def filter(func):
    def wrapper(self, *args, **kwargs):
        df = func(self, *args, **kwargs)
        for f in kwargs.get('filter_vals',[]):
            df = df[df[f]==1]
        return df.dropna() if not kwargs.get('filter_cols') else df[['up','down']+kwargs['filter_cols']].dropna()
    return wrapper

class Technicals:
    def __init__(self, df, **kwargs):
        """ kwargs --> overlays, indicators, ntiles, change_only, vals_only, include_historicals, include_time, filter_vals, filter_cols """
        self.df = self.build(df, **kwargs) if not kwargs.get('change_only') else self.change(df, **kwargs)

    @filter
    def build(self, df, **kwargs):
        overlays = Overlays(df, **kwargs).get() if kwargs.get('overlays',True) else []
        indicators = Indicators(df, **kwargs).get() if kwargs.get('indicators',True) else []
        return self.change(df, **kwargs).join(overlays+indicators) if not kwargs.get('include_historicals', True) else df.join(overlays+indicators)

    def change(self, df, **kwargs):
        df['up'], df['down'] = df['change'].apply(lambda x: 1 if x > 0 else 0), df['change'].apply(lambda x: 1 if x < 0 else 0)
        #df['up'], df['down'] = [0]+[1 if df.loc[i + 1, 'change'] > 0 else 0 for i in range(df.shape[0]-1)], [0]+[1 if df.loc[i + 1, 'change'] < 0 else 0 for i in range(df.shape[0]-1)]
        if kwargs.get('ntiles'):
            df = df.join(convert_ntile(df['changePercent'],n=kwargs.get('ntiles'), abs_val=True))
        return df[[col for col in df if np.isin(df[col].dropna().unique(), [0.0, 1.0]).all()]].fillna(0) if not kwargs.get('include_time') else df[[col for col in df if np.isin(df[col].dropna().unique(), [0.0, 1.0]).all() or col in ['date','minute']]].fillna(0)

#df = pd.read_csv('AMD_historicals_daily.csv')
#t = Technicals(df)
#df = Technicals(df, overlays=False, indicators=['RSI'], vals_only=False, include_historicals=False).df
#t.df.to_csv('AMD_technicals_daily.csv',index=False)
#df['up'] = [0,0] + [1 if df.loc[i-1, 'change'] > 0 else 0 for i in range(2,df.shape[0])]
#print(df)
"""PARAMS
- Technicals
    - df : historical df, used for Signals and Technicals
    - overlays : bool or list of overlays to include, used for Overlays
    - overlay_periods : any valid int
    - indicators : bool or list of indicators to include, used for Indicators
    - ntiles : int, used for Signals and Technicals
    - change_only : bool, only get the change frame
    - vals_only : bool, only get the indicator values
    - include_historicals : bool, keep the historicals df data
    - include_time : bool, keep the time of each record
    - filters : list of column names that are True (1) in a binary column, used for Technicals
"""



