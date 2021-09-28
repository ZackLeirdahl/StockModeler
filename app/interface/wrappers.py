import pandas as pd
import mpld3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter

def append_changes(func):
    def wrapper(self, df, **kwargs):
        df = func(self, df, **kwargs)
        if type(df) == bool:
            return False
        for m in ['volume','open_interest','implied_volatility']:
            df[m + '_change'] = df[m].diff()
            df[m + '_change_pct'] =  [0] + [round(100*(df.iloc[i,3 if m=='volume' else (5 if m == 'open_interest' else 7)] / df.iloc[i-1,0 if m=='volume' else (1 if m=='open_interest' else 2)]),2) for i in range(1,df.shape[0])]
        return df.reset_index()
    return wrapper

def plot(func):
    def wrapper(self):
        fig, ax = plt.subplots(figsize = (7,4))
        df = func(self)
        ax.plot(df[self.index], df[self.lines])
        ax.set(xlabel='time',ylabel=self.lines[0],title='{} {}'.format(self.symbol, self.lines[0]))
        return mpld3.fig_to_html(fig)
    return wrapper