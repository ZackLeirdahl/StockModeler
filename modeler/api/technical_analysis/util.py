import math
import sys
sys.setrecursionlimit(10000)
import numpy as np
import pandas as pd

def ema(series, periods):
    return series.ewm(span=periods, min_periods=periods).mean()

def average_up_dn(up_dn, series, position, n):
    if position >= len(list(series)):
        return up_dn
    else:
        up_dn.append((up_dn[-1]*(n-1)+series[position -1])/n)
        return average_up_dn(up_dn, series, position +1, n)

def convert_binary(series):
    return (series.apply(lambda x: 1 if x == 1 else 0), series.apply(lambda x: 1 if x == -1 else 0))

def convert_ntile(series, n=4, abs_val=False):
    df = pd.DataFrame(series)
    ntiles = pd.qcut(series if not abs_val else series.apply(lambda x: abs(x)), n, labels=[i+1 for i in range(n)], retbins=False, duplicates='drop')
    for i in range(n):
        df['_'.join([series.name,'nt',str(i+1)])] = ntiles.apply(lambda x: 1 if x==i+1 else 0)
    return df[['_'.join([series.name,'nt',str(i+1)]) for i in range(n)]]


