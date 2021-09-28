import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
from firebase import Firebase

def plot(func):
    def wrapper(self):
        df = func(self)
        #df.plot(kind=self.kind, linestyle=self.linestyle, subplots=self.subplots, stacked=self.stacked)
        plt.plot(df[self.index], df[self.lines], )
        plt.show()
        return None
    return wrapper

class Plotter:
    def __init__(self, *args, **kwargs):
        self.df = Firebase().get(args[0]) if not isinstance(args[0],pd.DataFrame) else args[0]
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

#df = pd.read_csv('AMD_technicals_daily.csv')

#Plotter(df, lines = ['rsi','wr','macd'],subplots=True)
#Plotter(df, lines = ['volume','vma_20','vma_50','vma_200'])
#Plotter('options/AMD_options_timeseries.csv', kind='bar', stacked=False, lines = ['call_volume','put_volume'])
Plotter('options/AMD_options_timeseries.csv', kind='line',linestyle='dotted', lines = ['volume'])
Plotter('options/AMD_options_timeseries.csv', kind='line',linestyle='dotted', lines = ['volume'])
""" kwargs
    num_rows : number of rows to include in plot 
    lines : a list of the column names to include in the line plot
    index : the index to set as the x axis on the line plot
    kind : 'line', ‘bar’,’barh’,’pie’,’scatter’,’kde’ etc which can be found in the docs.
    linestyle : ‘solid’, ‘dotted’, ‘dashed’ (applies to line graphs only)
    subplots : bool, if True will break into subplots - default is False
"""


""" TO DO
- create a method to create change% frame, use to compare multiple stocks
- create a method to autoscale the plot by setting the ylim
    - get the upper and lower limits of period, expand by a little bit: return tuple
- create a method to better label the x axis for time series
"""


""" df.plot

kind — ‘bar’,’barh’,’pie’,’scatter’,’kde’ etc which can be found in the docs.
color — Which accepts and array of hex codes corresponding sequential to each data series / column.
linestyle — ‘solid’, ‘dotted’, ‘dashed’ (applies to line graphs only)
xlim, ylim — specify a tuple (lower limit, upper limit) for which the plot will be drawn
legend— a boolean value to display or hide the legend
labels — a list corresponding to the number of columns in the dataframe, a descriptive name can be provided here for the legend
title — The string title of the plot

"""
"""plt.plot

Property	            Value Type
alpha	                float
animated	            [True | False]
antialiased or aa	    [True | False]
clip_box	            a matplotlib.transform.Bbox instance
clip_on	                [True | False]
clip_path	            a Path instance and a Transform instance, a Patch
color or c	            any matplotlib color
contains	            the hit testing function
dash_capstyle	        ['butt' | 'round' | 'projecting']
dash_joinstyle	        ['miter' | 'round' | 'bevel']
dashes	                sequence of on/off ink in points
data	                (np.array xdata, np.array ydata)
figure	                a matplotlib.figure.Figure instance
label	                any string
linestyle or ls	        [ '-' | '--' | '-.' | ':' | 'steps' | ...]
linewidth or lw	        float value in points
marker	                [ '+' | ',' | '.' | '1' | '2' | '3' | '4' ]
markeredgecolor or mec	any matplotlib color
markeredgewidth or mew	float value in points
markerfacecolor or mfc	any matplotlib color
markersize or ms	    float
markevery	            [ None | integer | (startind, stride) ]
picker	                used in interactive line selection
pickradius	            the line pick selection radius
solid_capstyle	        ['butt' | 'round' | 'projecting']
solid_joinstyle	        ['miter' | 'round' | 'bevel']
transform	            a matplotlib.transforms.Transform instance
visible	                [True | False]
xdata	                np.array
ydata	                np.array
zorder	                any number
"""