import pandas as pd
import numpy as np
import scipy.stats as si
from dateutil.parser import parse
from datetime import datetime

def user_input():
    print('Input challenge code from SMS')
    return str(input())   

def filter_measurements(df, **kwargs):
    for k, v in kwargs.items():
        df = df[df[k] == v] if k != 'strike_price' else df[df[k]==float(v)]
    return df

def chunked_list(_list, _chunk_size=50):
    for i in range(0, len(_list), _chunk_size):
        yield _list[i:i + _chunk_size]

def dte(exp):
    return (datetime.strptime(parse(exp).strftime('%m/%d/%Y'), '%m/%d/%Y') - datetime.strptime(datetime.now().strftime('%m/%d/%Y'), '%m/%d/%Y')).days

def black_scholes(p, s, t, r, iv, type = 'call'):
    """
    A method for getting the theoretical mark of an option.
    Parameters
    ----------
    p : float
        the current price of the stock
    s : float
        the strike price of the option
    t : float
        the time to maturity, expressed as (days to maturity / 365)
    r : float
        the risk-free interest rate, expressed as a decimal
    iv : float
        the implied volatility of the stock, expressed as a decimal
    type : str, optional
        the type of option, default is 'call'
    Returns
    -------
    float
        the theoretical value of the option
    """
    d1 = (np.log(p / s) + (r + 0.5 * iv ** 2) * t) / (iv * np.sqrt(t))
    d2 = (np.log(p / s) + (r - 0.5 * iv ** 2) * t) / (iv * np.sqrt(t))
    return (p * si.norm.cdf(d1, 0.0, 1.0) - s * np.exp(-r * t) * si.norm.cdf(d2, 0.0, 1.0)) if type == 'call' else (s * np.exp(-r * t) * si.norm.cdf(-d2, 0.0, 1.0) - p * si.norm.cdf(-d1, 0.0, 1.0))

def format_strike(strike):  
    return '.'.join([strike.split('.')[0], strike.split('.')[-1][0] + '000']) if len(strike.split('.')) > 1 else strike + '.0000'

def get_long_short_difference(df):
    return int(float(df[df['type']=='long']['quantity'].sum())) - int(float(df[df['type']=='short']['quantity'].sum()))

def get_max_quantity(df, option, exp_len):
    lsd = get_long_short_difference(df) if exp_len > 1 else 0
    max_quantity = int(float(df[df['option']==option]['quantity'])) if lsd > 0 or int(float(df[df['option']==option]['quantity'])) >= lsd else lsd
    return int(float(df[df['option']==option]['quantity'])) if exp_len == 1 else (max_quantity if max_quantity <= lsd else lsd)