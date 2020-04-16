import pandas as pd
from indicators import Indicators
from overlays import Overlays
from util import *

def filter(func):
    def wrapper(self, *args, **kwargs):
        df = func(self, *args, **kwargs)
        for f in kwargs.get('filter_vals',[]):
            df = df[df[f]==1]
        return df.dropna() if not kwargs.get('filter_cols') else df[['up','down']+kwargs['filter_cols']].dropna()
    return wrapper

class Technicals:
    def __init__(self, df, **kwargs):
        """ kwargs --> overlays, indicators, ntiles, change_only, filter_vals, filter_cols """
        self.df = self.build(df, **kwargs) if not kwargs.get('change_only') else self.change(df, **kwargs)

    @filter
    def build(self, df, **kwargs):
        overlays = Overlays(df, **kwargs).get() if kwargs.get('overlays',True) else []
        indicators = Indicators(df, **kwargs).get() if kwargs.get('indicators',True) else []
        return self.change(df, **kwargs).join(overlays+indicators)

    def change(self, df, **kwargs):
        df['up'], df['down'] = df['change'].apply(lambda x: 1 if x > 0 else 0), df['change'].apply(lambda x: 1 if x < 0 else 0)
        if kwargs.get('ntiles'):
            df = df.join(convert_ntile(df['changePercent'],n=4, abs_val=True))
        return df[[col for col in df if np.isin(df[col].dropna().unique(), [0.0, 1.0]).all()]].fillna(0)

df = pd.read_csv('storage\\historicals\\AMD_daily_historicals.csv')
print(convert_ntile(df['changePercent'], abs_val=True))
#df = Technicals(df, overlays=['SMA'], overlay_periods=[10], indicators=False, ntiles=4, filter_cols=['sma_10_pctOfval_nt_4']).df
#print(df)
#print(df)
"""PARAMS
- Technicals
    - df : historical df, used for Signals and Technicals
    - overlays : bool or list of overlays to include, used for Overlays
    - overlay_periods : any valid int
    - indicators : bool or list of indicators to include, used for Indicators
    - ntiles : int, used for Signals and Technicals
    - filters : list of column names that are True (1) in a binary column, used for Technicals
"""



