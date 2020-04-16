import inspect, uuid, json, time, os
import pandas as pd
from functools import wraps
from datetime import datetime
from dateutil.parser import parse
try:
    from util import fullpath
    from endpoints import stock
except:
    from .util import fullpath
    from .endpoints import stock

""" Client Wrappers """
def authorize(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.access_token:
            self.headers["Authorization"] = "Bearer {0}".format(self.access_token)
        return func(self, *args, **kwargs)
    return wrapper

def post_login(func):
    def wrapper(self, *args, **kwargs):
        data = func(self, *args, **kwargs)
        del self.headers['Content-Type']
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
        self.payload = {'client_id': 'c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS' ,'device_token': str(uuid.uuid4()),'expires_in': 86400,'grant_type': 'password','password': self.password,'scope': 'internal','username': self.username,'challenge_type': 'sms'}
        self.headers['Content-Type'] = 'application/json'
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
        self.id = data['id']
        self.expiration_dates = data['expiration_dates']
        self.num_threads = len(self.expiration_dates)
        self.dfs = []
        list(map(self.q.put, self.expiration_dates))
        return data
    return wrapper

def append_timestamp(func):
    def wrapper(self):
        df = func(self)
        time_stamp = int(datetime.timestamp(datetime.now().replace(microsecond=0)))
        df['time_stamp'] = [time_stamp for i in range(df.shape[0])]
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
        return func(self, *args, **kwargs)[['strike_price','volume','open_interest','expiration_date','mark_price']]
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
        orders = func(self, **kwargs)
        filters = {k: v for k, v in kwargs.items() if k in ['state','opening_strategy','chain_symbol']}
        results =  [list(filter(lambda x: x[k] == v, orders)) for k, v in filters.items()][0]
        if kwargs.get('ids'):
            return [o['id'] for o in results]
        return results
    return wrapper

def filter_stock_orders(func):
    def wrapper(self, **kwargs):
        orders = func(self, **kwargs)
        filters = {k if k != 'symbol' else 'instrument': v if k != 'symbol' else self.client.get(stock(v))['results'][0]['url'] for k, v in kwargs.items() if k in ['symbol', 'type','state']}
        results = [list(filter(lambda x: x[k] == v, orders)) for k, v in filters.items()][0]
        if kwargs.get('ids'):
            return [o['id'] for o in results]
        return results
    return wrapper

def filter_options_positions(func):
    def wrapper(self, **kwargs):
        options = func(self, **kwargs)
        filters = {k if k != 'symbol' else 'chain_symbol': v for k, v in kwargs.items() if k in ['symbol', 'type']}
        results = [list(filter(lambda x: x[k] == v, options)) for k, v in filters.items()][0] if filters else options
        if kwargs.get('ids'):
            return [o['option'][:-1].split('/')[-1] for o in results]
        return results
    return wrapper