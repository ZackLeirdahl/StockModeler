import pandas as pd
import numpy as np
try:
    from signals import Signal
    from util import *
except:
    from .signals import Signal
    from .util import *

OVERLAYS = ['SMA', 'EMA', 'VMA']
PERIODS = [10, 20, 50, 100, 200]

class _Overlay(Signal):
    def __init__(self, df, **kwargs):
        Signal.__init__(self, df, **kwargs)

    def additional_columns(self, df):
        col = df[self.name]
        dx =  [np.nan for i in range(self.n)] + [1 if col[i-1] < col[i] else -1 for i in range(self.n, len(col))]
        inflection = [np.nan for i in range(self.n)] + [1 if dx[i-1] < dx[i] else (-1 if dx[i-1] > dx[i] else 0) for i in range(self.n, len(col))]
        pct_of_val = [np.nan for i in range(self.n)] + [round(100*(col[i]/self.series[i]),2) for i in range(self.n, len(col))]
        df[self.name+'_dx'], df[self.name+'_inflx'], df[self.name+'_pctOfval'] = dx, inflection, pct_of_val
        df[self.name+'_dx_up'], df[self.name+'_dx_down'] = convert_binary(df[self.name+'_dx'])
        df[self.name+'_inflx_up'], df[self.name+'_inflx_down'] = convert_binary(df[self.name+'_inflx'])
        if self.ntiles:
            df = df.join([convert_ntile(df[self.name],n=self.ntiles),convert_ntile(df[self.name+'_pctOfval'],n=self.ntiles)])
        return df
    
class SMA(_Overlay):
    def __init__(self, df, **kwargs):
        _Overlay.__init__(self, df, **kwargs)
        self.name, self.n, self.series = '_'.join(['sma',str(kwargs.get('n',10))]), kwargs.get('n',10), df['close']
    
    def calculate(self):
        return pd.Series(data=self.series.rolling(window=self.n, min_periods=self.n).mean(), name=self.name)

class EMA(_Overlay):
    def __init__(self, df, **kwargs):
        _Overlay.__init__(self, df, **kwargs)
        self.name, self.n, self.series = '_'.join(['ema',str(kwargs.get('n',10))]), kwargs.get('n',10), df['close']
    
    def calculate(self):
        return pd.Series(data=self.series.ewm(span=self.n, min_periods=self.n, adjust=False).mean(),name=self.name)

class VMA(_Overlay):
    def __init__(self, df, **kwargs):
        _Overlay.__init__(self, df, **kwargs)
        self.name, self.n, self.series = '_'.join(['vma',str(kwargs.get('n',10))]), kwargs.get('n',10), df['volume']
    
    def calculate(self):
        return pd.Series(data=self.series.rolling(self.n, min_periods=self.n).mean(),name=self.name)

class Overlays:
    def __init__(self, df, **kwargs):
        self.df, self.kwargs = df, kwargs
        self.overlays = OVERLAYS if kwargs.get('overlays', True) is True else kwargs['overlays']
        self.periods = [period for period in PERIODS if period < df.shape[0]] if not kwargs.get('overlay_periods') else kwargs['overlay_periods']

    def get(self):
        return [eval(overlay)(self.df, n=period, **self.kwargs).run() for overlay in self.overlays for period in self.periods]
