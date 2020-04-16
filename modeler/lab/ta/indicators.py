import numpy as np
import pandas as pd
from signals import Signal
from util import *

INDICATORS = ['RSI', 'WR', 'AO', 'AROON', 'BB', 'CCI', 'CMF', 'KC', 'KST', 'MACD', 'MFI', 'STOCH_D', 'STOCH_K', 'TRIX', 'TSI', 'UO'] #['ATR', 'OBV']

class _Indicator(Signal):
    def __init__(self, df, **kwargs):
        Signal.__init__(self, df, **kwargs)
        self.open, self.close, self.high, self.low, self.volume = df['open'], df['close'], df['high'], df['low'], df['volume']
    
    def additional_columns(self, df):
        if self.name not in ['bb','kc']:
            sig = pd.Series(self.signal(df[self.name] if self.name in list(df.columns) else df[self.name+'_up'] - df[self.name+'_down']))
            df[self.name + '_buy'], df[self.name + '_sell'] = convert_binary(sig)
        if self.name in list(df.columns):
            max_val = df[self.name].max()
            df[self.name + '_pctOfmax'] = df[self.name].apply(lambda x: x /max_val)
            df[self.name + '_delta'] = df[self.name].pct_change().apply(lambda x: round(100*x,2))
            if self.ntiles:
                df = df.join([convert_ntile(df[self.name],n=self.ntiles),convert_ntile(df[self.name + '_delta'],n=self.ntiles,abs_val=True),convert_ntile(df[self.name + '_pctOfmax'],n=self.ntiles)])
        return df

class RSI(_Indicator):
    def __init__(self, df, **kwargs):
        _Indicator.__init__(self, df, **kwargs)
        self.name, self.n, self.ind_type = 'rsi', kwargs.get('n',14), 'momentum'

    def calculate(self):
        diff = self.close.diff(1)
        which_dn = diff < 0
        up, dn = diff, diff*0
        up[which_dn], dn[which_dn] = 0, -up[which_dn]
        avg_up = average_up_dn([np.nan for i in range(self.n)] + [up[1:self.n+1].mean()], up, self.n+2, self.n)
        avg_dn = average_up_dn([np.nan for i in range(self.n)] + [dn[1:self.n+1].mean()], dn, self.n+2, self.n)
        rs = [avg_up[i]/avg_dn[i] for i in range(len(avg_up))]
        return pd.Series([100 - (100/(1+rs[i])) for i in range(len(rs))], name=self.name)

    def signal(self, column):
        return column.apply(lambda x: 1 if x < 30 else (-1 if x > 70 else 0))

class MFI(_Indicator):
    def __init__(self, df, **kwargs):
        _Indicator.__init__(self, df, **kwargs)
        self.name, self.n, self.ind_type = 'mfi', kwargs.get('n',14), 'momentum'
    
    def calculate(self):
        df = pd.DataFrame([self.high, self.low, self.close, self.volume]).T
        df['u_or_d'], df['1p_pos'], df['1p_neg'] = 0.0, 0.0, 0.0
        df.loc[(df['close'] > df['close'].shift(1, fill_value=df['close'].mean())), 'u_or_d'] = 1
        df.loc[(df['close'] < df['close'].shift(1, fill_value=df['close'].mean())), 'u_or_d'] = 2
        mf = ((df['high'] + df['low'] + df['close']) / 3.0) * df['volume']
        df.loc[df['u_or_d'] == 1, '1p_pos'] = mf
        df.loc[df['u_or_d'] == 2, '1p_neg'] = mf
        return pd.Series((100 - (100 / (1 + (df['1p_pos'].rolling(self.n, min_periods=0).sum() / df['1p_neg'].rolling(self.n, min_periods=0).sum())))), name=self.name)

    def signal(self, column):
        return column.apply(lambda x: 1 if x < 20  else (-1 if x > 80 else 0))

class TSI(_Indicator):
    def __init__(self, df, **kwargs):
        _Indicator.__init__(self, df, **kwargs)
        self.name, self.n, self.ind_type = 'tsi', kwargs.get('n',25), 'momentum'

    def calculate(self):
        m = self.close - self.close.shift(1, fill_value=self.close.mean())
        return pd.Series((m.ewm(self.n).mean().ewm(13).mean() / abs(m).ewm(self.n).mean().ewm(13).mean()) * 100, name=self.name)

    def signal(self, column):
        return column.apply(lambda x: 1 if x < -25  else (-1 if x > 25 else 0))

class UO(_Indicator):
    def __init__(self, df, **kwargs):
        _Indicator.__init__(self, df, **kwargs)
        self.name, self.n, self.ind_type = 'uo', kwargs.get('n',28), 'momentum'
    
    def calculate(self):
        min_l_or_pc = self.close.shift(1, fill_value=self.close.mean()).combine(self.low, min)
        bp = self.close - min_l_or_pc
        tr = self.close.shift(1, fill_value=self.close.mean()).combine(self.high, max) - min_l_or_pc
        return pd.Series(100.0 * ((4 * bp.rolling(7, min_periods=0).sum() / tr.rolling(7, min_periods=0).sum()) + (2 * bp.rolling(14, min_periods=0).sum() / tr.rolling(14, min_periods=0).sum()) + (1 * bp.rolling(self.n, min_periods=0).sum() / tr.rolling(self.n, min_periods=0).sum())) / (4 + 2 + 1), name=self.name)

    def signal(self, column):
        return column.apply(lambda x: 1 if x < 30  else (-1 if x > 70 else 0))

class STOCH_K(_Indicator):
    def __init__(self, df, **kwargs):
        _Indicator.__init__(self, df, **kwargs)
        self.name, self.n, self.ind_type = 'stoch_k', kwargs.get('n',14), 'momentum'
    
    def calculate(self):
        smin = self.low.rolling(self.n, min_periods=0).min()
        return pd.Series(100 * (self.close - smin) / (self.high.rolling(self.n, min_periods=0).max() - smin), name=self.name)

    def signal(self, column):
        return column.apply(lambda x: 1 if x < 20  else (-1 if x > 80 else 0))

class STOCH_D(_Indicator):
    def __init__(self, df, **kwargs):
        _Indicator.__init__(self, df, **kwargs)
        self.name, self.n, self.ind_type = 'stoch_d', kwargs.get('n',14), 'momentum'
    
    def calculate(self):
        smin = self.low.rolling(self.n, min_periods=0).min()
        stoch_k = pd.Series(100 * (self.close - smin) / (self.high.rolling(self.n, min_periods=0).max() - smin), name='stoch_k')
        return pd.Series(stoch_k.rolling(3, min_periods=0).mean(), name=self.name)

    def signal(self, column):
        return column.apply(lambda x: 1 if x < 20  else (-1 if x > 80 else 0))

class WR(_Indicator):
    def __init__(self, df, **kwargs):
        _Indicator.__init__(self, df, **kwargs)
        self.name, self.n, self.ind_type = 'wr', kwargs.get('n',14), 'momentum'
    
    def calculate(self):
        hh = self.high.rolling(self.n, min_periods=0).max()
        return pd.Series(-100 * (hh - self.close) / (hh - self.low.rolling(self.n, min_periods=0).min()), name=self.name)

    def signal(self, column):
        return column.apply(lambda x: 1 if x < -80  else (-1 if x > -20 else 0))

class AO(_Indicator):
    def __init__(self, df, **kwargs):
        _Indicator.__init__(self, df, **kwargs)
        self.name, self.n, self.ind_type = 'ao', kwargs.get('n',34), 'momentum'
    
    def calculate(self):
        mp = 0.5 * (self.high + self.low)
        return pd.Series(mp.rolling(5, min_periods=0).mean() - mp.rolling(self.n, min_periods=0).mean(), name=self.name)

    def signal(self, column):
        return [0 for i in range(self.n)] + [1 if column[i-1] < 0 and column[i] > 0 else (-1 if column[i-1] > 0 and column[i] < 0 else 0) for i in range(self.n,len(column))]

class MACD(_Indicator):
    def __init__(self, df, **kwargs):
        _Indicator.__init__(self, df, **kwargs)
        self.name, self.n, self.decimal, self.ind_type = 'macd', kwargs.get('n',26), 3, 'trend'
    
    def calculate(self):
        return pd.Series(ema(self.close, 12) - ema(self.close, self.n), name=self.name)

    def signal(self, column):
        macd_diff = column - ema(column, 9)
        return [None for i in range(self.n)] + [1 if macd_diff[i-1] < 0 and macd_diff[i] > 0 else (-1 if macd_diff[i-1] > 0 and macd_diff[i] < 0 else 0) for i in range(self.n,len(macd_diff))]

class TRIX(_Indicator):
    def __init__(self, df, **kwargs):
        _Indicator.__init__(self, df, **kwargs)
        self.name, self.n, self.decimal, self.ind_type = 'trix', kwargs.get('n',15), 3, 'trend'
    
    def calculate(self):
        ema3 = ema(ema(ema(self.close, self.n), self.n), self.n)
        return pd.Series(((ema3 - ema3.shift(1, fill_value=ema3.mean())) / ema3.shift(1, fill_value=ema3.mean()))*100, name=self.name)

    def signal(self, column):
        return [0 for i in range(43)] + [1 if column[i-1] < 0 and column[i] > 0 else (-1 if column[i-1] > 0 and column[i] < 0 else 0) for i in range(43,len(column))]

class CCI(_Indicator):
    def __init__(self, df, **kwargs):
        _Indicator.__init__(self, df, **kwargs)
        self.name, self.n, self.ind_type = 'cci', kwargs.get('n',20), 'trend'
    
    def calculate(self):
        pp = (self.high + self.low + self.close) / 3.0
        return pd.Series(((pp - pp.rolling(self.n, min_periods=0).mean()) / (0.015 * pp.rolling(self.n, min_periods=0).apply(lambda x : np.mean(np.abs(x-np.mean(x))), True))), name=self.name)

    def signal(self, column):
        return [0] + [1 if column[i-1] < 100  and column[i] > 100 else (-1 if column[i-1] > -100  and column[i-1] < -100 else 0) for i in range(1,len(column))]

class KST(_Indicator):
    def __init__(self, df, **kwargs):
        _Indicator.__init__(self, df, **kwargs)
        self.name, self.n, self.ind_type = 'kst', kwargs.get('n',30), 'trend'
    
    def calculate(self):
        rocma1 = ((self.close - self.close.shift(10, fill_value=self.close.mean())) / self.close.shift(10, fill_value=self.close.mean())).rolling(10, min_periods=0).mean()
        rocma2 = ((self.close - self.close.shift(15, fill_value=self.close.mean())) / self.close.shift(15, fill_value=self.close.mean())).rolling(10, min_periods=0).mean()
        rocma3 = ((self.close - self.close.shift(20, fill_value=self.close.mean())) / self.close.shift(20, fill_value=self.close.mean())).rolling(10, min_periods=0).mean()
        rocma4 = ((self.close - self.close.shift(30, fill_value=self.close.mean())) / self.close.shift(30, fill_value=self.close.mean())).rolling(15, min_periods=0).mean()
        return pd.Series(100 * (rocma1 + 2 * rocma2 + 3 * rocma3 + 4 * rocma4), name=self.name)

    def signal(self, column):
        kst_sig = column.rolling(9, min_periods=0).mean()
        return [0 for i in range(9)] + [1 if kst_sig[i-1] < 0 and kst_sig[i] > 0 else (-1 if kst_sig[i-1] > 0 and kst_sig[i] < 0 else 0) for i in range(9,len(kst_sig))]

class AROON(_Indicator):
    def __init__(self, df, **kwargs):
        _Indicator.__init__(self, df, **kwargs)
        self.name, self.n, self.ind_type = 'aroon', kwargs.get('n',25), 'trend'

    def calculate(self):
        aroon_up = self.close.rolling(self.n, min_periods=0).apply(lambda x: float(np.argmax(x) + 1) / self.n * 100, raw=True)
        aroon_down = self.close.rolling(self.n, min_periods=0).apply(lambda x: float(np.argmin(x) + 1) / self.n * 100, raw=True)
        return pd.DataFrame([pd.Series(aroon_up,name=self.name + '_up'), pd.Series(aroon_down,name=self.name + '_down')]).transpose()

    def signal(self, column):
        return [0] + [1 if column[i-1] < 0 and column[i] > 0 else (-1 if column[i-1] > 0 and column[i] < 0 else 0) for i in range(1,len(column))]

class ATR(_Indicator):
    def __init__(self, df, **kwargs):
        _Indicator.__init__(self, df, **kwargs)
        self.name, self.n, self.decimal, self.ind_type = 'atr', kwargs.get('n',14), 3, 'volatility'

    def calculate(self):
        cs = self.close.shift(1)
        tr = self.high.combine(cs, max) - self.low.combine(cs, min)
        atr = np.zeros(len(self.close))
        atr[0] = tr[1::].mean()
        for i in range(1, len(atr)):
            atr[i] = (atr[i-1] * (self.n-1) + tr.iloc[i]) / float(self.n)
        return pd.Series(pd.Series(data=atr, index=tr.index), name='atr')

    def signal(self, column):
        return column.apply(lambda x: 1 if x < 1 else 0)

class BB(_Indicator):
    def __init__(self, df, **kwargs):
        _Indicator.__init__(self, df, **kwargs)
        self.name, self.n, self.ind_type = 'bb', kwargs.get('n',20), 'volatility'

    def calculate(self):
        df = pd.DataFrame([self.close]).transpose()
        mavg, mstd = self.close.rolling(self.n).mean(), self.close.rolling(self.n).std()
        hband, lband = mavg + 2 * mstd, mavg - 2 * mstd
        df['hband'], df['lband'] = 0.0, 0.0
        df.loc[self.close > hband, 'hband'] = 1.0
        df.loc[self.close < lband, 'lband'] = 1.0
        return pd.DataFrame([pd.Series(df['hband'],name='bb_sell'), pd.Series(df['lband'],name='bb_buy')]).transpose()

class KC(_Indicator):
    def __init__(self, df, **kwargs):
        _Indicator.__init__(self, df, **kwargs)
        self.name, self.n, self.ind_type = 'kc', kwargs.get('n',10), 'volatility'

    def calculate(self):
        df = pd.DataFrame([self.close]).transpose()
        hband, lband = ((4 * self.high) - (2 * self.low) + self.close) / 3.0, ((-2 * self.high) + (4 * self.low) + self.close) / 3.0
        df['hband'], df['lband'] = 0.0, 0.0
        df.loc[self.close > hband, 'hband'] = 1.0
        df.loc[self.close < lband, 'lband'] = 1.0
        return pd.DataFrame([pd.Series(df['hband'],name='kc_sell'), pd.Series(df['lband'],name='kc_buy')]).transpose()

class OBV(_Indicator):
    def __init__(self, df, **kwargs):
        _Indicator.__init__(self, df, **kwargs)
        self.name, self.n, self.ind_type = 'obv', kwargs.get('n',2), 'volume'

    def calculate(self):
        df = pd.DataFrame([self.close, self.volume]).transpose()
        df['obv'] = np.nan
        c1, c2 = self.close < self.close.shift(1), self.close > self.close.shift(1)
        if c1.any():
            df.loc[c1, 'obv'] = - self.volume
        if c2.any():
            df.loc[c2, 'obv'] = self.volume
        return pd.Series(df['obv'].cumsum(),name=self.name)

    def signal(self, column):
        return [np.nan for i in range(self.n)] + [1 if column[i-1] < column[i] else -1 for i in range(self.n, len(column))]

class CMF(_Indicator):
    def __init__(self, df, **kwargs):
        _Indicator.__init__(self, df, **kwargs)
        self.name, self.n, self.decimal, self.ind_type = 'cmf', kwargs.get('n',20), 3, 'volume'

    def calculate(self):
        mfv = ((self.close - self.low) - (self.high - self.close)) / (self.high - self.low)
        mfv = mfv.fillna(0.0) * self.volume
        return pd.Series((mfv.rolling(self.n, min_periods=0).sum() / self.volume.rolling(self.n, min_periods=0).sum()),name=self.name)

    def signal(self, column):
        return column.apply(lambda x:  1 if x > .05  else (-1 if x < -.05 else 0))

class Indicators:
    def __init__(self, df, **kwargs):
        self.df, self.kwargs = df, kwargs 
        self.indicators = INDICATORS if kwargs.get('indicators', True) is True else kwargs['indicators']

    def get(self, **kwargs):
        return [eval(indicator)(self.df, **self.kwargs).run() for indicator in self.indicators]


