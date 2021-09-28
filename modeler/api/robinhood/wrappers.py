import inspect, uuid, json, time, os
import pandas as pd
from functools import wraps
from datetime import datetime
from dateutil.parser import parse
try:
    from endpoints import stock
except:
    from .endpoints import stock

""" Client Wrappers """
def authorize(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.access_token:
            self.HEADERS["Authorization"] = "Bearer {0}".format(self.access_token)
        return func(self, *args, **kwargs)
    return wrapper

def post_login(func):
    def wrapper(self, *args, **kwargs):
        data = func(self, *args, **kwargs)
        del self.HEADERS['Content-Type']
        self.account_id = '5RW21209'
        self.credentials = {'account_id': self.account_id, 'access_token': data['access_token'], 'refresh_token': data['refresh_token'], 'scope': data['scope'], 'token_type': data['token_type'], 'device_token': None}
        self.access_token = data['access_token']
        if not self.authenticated:
            with open('robinhood_auth.json', 'w') as f:
                f.write(json.dumps(self.credentials, indent=4))
            self.authenticated = True
        return self.authenticated 
    return wrapper

def pre_login(func):
    @wraps(func)
    def wrapper(self):
        with open('robinhood_cred.json', 'r') as f:
            creds = json.loads(f.read())
        self.payload = {'client_id': 'c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS' ,'device_token': str(uuid.uuid4()),'expires_in': 86400,'grant_type': 'password','password': creds['password'],'scope': 'internal','username': creds['username'],'challenge_type': 'sms'}
        self.HEADERS['Content-Type'] = 'application/json'
        if os.path.exists('robinhood_auth.json'):
            if (int(time.time()) - int(os.path.getmtime('robinhood_auth.json')))/3600 > 22:
                os.remove('robinhood_auth.json')
                self.authenticated = False
            else:
                self.authenticated = True
        return func(self)
    return wrapper

""" Chain Wrappers """
def populate_queue(func):
    def wrapper(self):
        data = func(self)
        self.id, self.expiration_dates, self.num_threads, self.dfs = data['id'], data['expiration_dates'], len(data['expiration_dates']), []
        list(map(self.q.put, self.expiration_dates))
        return data
    return wrapper

def append_fields(func):
    def wrapper(self):
        df = func(self)
        if isinstance(df, pd.DataFrame):
            iloc_ask, iloc_bid, iloc_vol, iloc_oi, time_stamp = list(df.columns).index('ask_price'), list(df.columns).index('bid_price'), list(df.columns).index('volume'), list(df.columns).index('open_interest'), int(datetime.timestamp(datetime.now().replace(microsecond=0)))
            df['time_stamp'], df['bid_ask_spread'], df['vol_oi_ratio'] = [time_stamp for i in range(df.shape[0])], [round(float(df.iloc[i,iloc_ask]) - float(df.iloc[i,iloc_bid]),3) for i in range(df.shape[0])], [round(float(df.iloc[i,iloc_vol]) / float(df.iloc[i,iloc_oi]),3) if float(df.iloc[i,iloc_oi]) > 0 else 0 for i in range(df.shape[0])]
        return df
    return wrapper

def latest_price(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        s = self.client.get(stock(self.symbol))['results'][0]
        self.price = float(self.client.get(s['quote'])['last_trade_price'])
        return func(self, *args, **kwargs)
    return wrapper

def filter_fields(func):
    def wrapper(self, *args, **kwargs):
        return func(self, *args, **kwargs)[['type','strike_price','volume','open_interest','expiration_date','mark_price']]
    return wrapper

def filter_fields_liquid(func):
    def wrapper(self, *args, **kwargs):
        return func(self, *args, **kwargs)[['type','expiration_date','strike_price','volume','open_interest','mark_price','bid_ask_spread','vol_oi_ratio','high_fill_rate_buy_price','high_fill_rate_sell_price','low_fill_rate_buy_price','low_fill_rate_sell_price','id','time_stamp']]
    return wrapper

""" Measurement Wrappers """
def clean_frame(func):
    def wrapper(self, **kwargs):
        df = func(self, **kwargs)
        if kwargs.get('dummy'):
            df['volume'] = df['volume'].apply(lambda x: 0)
        self.df = df[~df['expiration_date'].isin([exp for exp in df['expiration_date'].unique() if parse(exp) < datetime.today()])]
        return {'root': self.root, 'descriptor': self.interval, 'df': self.df}
    return wrapper

""" Portfolio Wrappers """
def filter_option_orders(func):
    def wrapper(self, **kwargs):
        orders, filters = func(self, **kwargs), {k: v for k, v in kwargs.items() if k in ['state','opening_strategy','chain_symbol']}
        results =  pd.DataFrame([list(filter(lambda x: x[k] == v, orders)) for k, v in filters.items()][0]) if kwargs else pd.DataFrame(orders)
        if kwargs.get('ids'):
            return results['id'].to_list()
        results['option'] = results['legs'].apply(lambda x: x[0]['option'])
        return results.sort_values(by=['created_at'], ascending=False)
    return wrapper

def filter_stock_orders(func):
    def wrapper(self, **kwargs):
        orders, filters = func(self, **kwargs), {k if k != 'symbol' else 'instrument': v if k != 'symbol' else self.client.get(stock(v))['results'][0]['url'] for k, v in kwargs.items() if k in ['symbol', 'type','state']}
        results = [list(filter(lambda x: x[k] == v, orders)) for k, v in filters.items()][0]
        if kwargs.get('ids'):
            return [o['id'] for o in results]
        return results
    return wrapper

def filter_options_positions(func):
    def wrapper(self, **kwargs):
        options, filters = func(self, **kwargs), {k if k != 'symbol' else 'chain_symbol': v for k, v in kwargs.items() if k in ['symbol', 'type']}
        results = pd.DataFrame([list(filter(lambda x: x[k] == v, options)) for k, v in filters.items()][0] if filters else options)
        if kwargs.get('ids'):
            results['id'] = results['option'].apply(lambda x: x[:-1].split('/')[-1])
            results['instrument'], results['side'] = results['option'], results['type']
            return results[['id','instrument','side','quantity']]
        return results
    return wrapper

def format_stock_positions(func):
    def wrapper(self):
        df = func(self)
        if df.shape[1] == 1:
            return None
        df = df[['symbol','equity','quantity','average_buy_price']]
        df['equity'], df['quantity'], df['average_buy_price'] = df['equity'].apply(lambda x: round(x,2)), df['quantity'].apply(lambda x: int(float(x))), df['average_buy_price'].apply(lambda x: round(float(x),2))
        df['gain'] = [df.loc[i,'quantity'] * ((df.loc[i,'equity']/df.loc[i,'quantity']) - df.loc[i,'average_buy_price']) for i in range(df.shape[0])]
        df['gain_percent'] = [round(100*(df.loc[i,'gain'] /df.loc[i,'equity']),3) for i in range(df.shape[0])]
        return df
    return wrapper