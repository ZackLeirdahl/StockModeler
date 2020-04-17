import pandas as pd
import matplotlib.pyplot as plt
from firebase import Firebase

def get_line_df(uri, num_rows=None, index='minute', lines=['open','high','low','close']):
    df = Firebase().get(uri).head(num_rows)[[index]+lines] if num_rows else Firebase().get(uri)[[index]+lines]
    df.index = df[index]
    return df

## 1 column bar ##
#df = Firebase().get('historicals/AMD_historicals_30.csv')
#df['volume'].plot(kind='bar')
#plt.show()

df = Firebase().get('historicals/AMD_historicals_daily.csv')
df = get_line_df('historicals/AMD_historicals_daily.csv', index='date')
df.plot()
plt.show()


#df = get_line_df('historicals/AMD_historicals_daily.csv', num_rows=50, lines=['high','low'])
#df.plot(title='AMD 30 Minute', ylim=(47,51))
#plt.show()

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