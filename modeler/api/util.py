from dateutil.parser import parse
from datetime import date, datetime

def is_date(string):
    try:
        parse(string, fuzzy=False)
        return True
    except:
        return False

def find_range(string):
    """
    A method for finding the range value to use for the fetching of historical prices from IEX API.
    Parameters
    ----------
    string : str
        the date string to parse for the range
    Returns
    -------
    str
        the range to use for fetching historical prices from IEX API.
    """
    weekday = parse(string, fuzzy=False).weekday()
    num_days = date.today().toordinal() - date.toordinal(parse(string, fuzzy=False))
    if num_days + weekday <= 5:
        return '5d'
    if ceil(1 + ((num_days - (5 - weekday)))/7) <= 4:
        return '1m'
    return '3m'  

def get_last_week_dates(last_date=None):
    """A method to get the string formatted dates for the last 5 trading days
    Parameters
    ----------
    last_date : str, optional
        the str of the date to start from, if None, will return the last 5 trading days (default is None)
    Returns
    -------
    list
        a list of the last 5 trading days or n trading days since last_date, formatted as 'YYYYMMDD'
    """
    ords = [parse(last_date).toordinal() + (i + 1)  for i in range((date.today().toordinal() -1) - parse(last_date).toordinal()) if date.fromordinal(parse(last_date).toordinal() + (i + 1)).weekday() not in [5,6]] if is_date(last_date) else  [(date.today().toordinal() - 7) + i for i in range(7) if date.fromordinal((date.today().toordinal() - 7) + i).weekday() not in [5,6]]
    return [date.fromordinal(ord).strftime('%Y%m%d') for ord in ords] if len(ords) < 5 else [date.fromordinal(ord).strftime('%Y%m%d') for ord in ords]#[-5:]

def time_ordinal():
    return datetime.today().toordinal()

def convert_timestamp(df, **kwargs):
    df['time_stamp'] = df['time_stamp'].apply(lambda x: datetime.fromtimestamp(x))
    return df[df['time_stamp'] == list(df['time_stamp'].unique())[-1]] if kwargs.get('last_time_stamp', True) else df

def number_timestamps(df):
    ts = list(df['time_stamp'].unique())
    zts = dict(zip(ts,[k[:10]+'_'+str(v+1) for k, v in dict(zip(list(df['time_stamp'].apply(lambda x: str(datetime.fromtimestamp(x))).unique()),[i for i in range(len(ts))])).items()]))
    df['time_stamp'] = df['time_stamp'].apply(lambda x: zts[x])
    return df