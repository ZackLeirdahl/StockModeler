import uuid, datetime, json
import pandas as pd
try:
    from endpoints import *
    from util import chunked_list
except:
    from .endpoints import *
    from .util import chunked_list

class ClientMethods(object):

    @classmethod
    def fetch_price(cls, client, symbol):
        now = datetime.datetime.now()
        return float(client.get(client.get(stock(symbol))['results'][0]['quote'])['last_trade_price']) if not ((now.hour > 14 or now.hour < 8) or (now.hour == 8 and now.minute < 30)) else float(client.get(client.get(stock(symbol))['results'][0]['quote'])['last_extended_hours_trade_price'])

    @classmethod
    def fetch_by_expiration(cls, client, chain_id, expiration_dates=[]):
        option_data = pd.DataFrame(client.get(options(), params={'chain_id': chain_id, 'expiration_dates': ','.join(expiration_dates)})['results'])
        market_data = pd.DataFrame(cls.market_data_by_ids(client, list(option_data['id'].unique())))
        return market_data.merge(option_data, left_on='instrument', right_on='url')
    
    @classmethod
    def fetch_by_id(cls, client, id, market_data=True):
        data = client.get(options(),params={'ids':id})['results'][0]
        return {**cls.market_data_by_url(client, data['url']), **data} if market_data else data

    @classmethod
    def market_data_by_url(cls, client, url):
        return client.get(option_marketdata(), params={'instruments': url})['results'][0]

    @classmethod
    def fetch_by_ids(cls, client, ids):
        return client.get(options(),params={'ids':','.join(ids)})['results']

    @classmethod
    def market_data_by_ids(cls, client, ids):
        results = []
        for _urls in chunked_list(["{}{}/".format(options(), _id) for _id in ids], 50):
            res = client.get(option_marketdata(), params={'instruments': ','.join(_urls)})
            if res:
                results.extend(res['results'])
        return [r for r in results if r is not None]
    
    @classmethod
    def fetch_account(cls, client):
        return client.get(accounts())['results'][0]
    
    @classmethod
    def fetch_portfolio(cls, client):
        return client.get(portfolio(cls.fetch_account(client)['account_number']))

    @classmethod
    def fetch_option_positions(cls, client):
        positions = {option['option'].split('/')[:-1][-1]: {k: v for k, v in option.items() if k in ['option','average_price','chain_symbol','type','id','quantity']} for option in list(filter(lambda p: float(p["quantity"]) > 0.0, client.get(option_positions())['results']))}
        mkt_data = {option['instrument'].split('/')[:-1][-1]: {k : v for k, v in option.items() if k in ['volume', 'implied_volatility', 'open_interest','mark_price']} for option in cls.market_data_by_ids(client, list(positions.keys()))}
        option_data = {option['id']: {k : v for k, v in option.items() if k in ['strike_price','expiration_date']} for option in cls.fetch_by_ids(client, positions.keys())}
        return [{**v, **mkt_data[k], **option_data[k]} for k, v in positions.items()]

    @classmethod
    def fetch_stock_positions(cls, client):
        positions = {client.get(stock['instrument'])['symbol']: stock for stock in list(filter(lambda x: float(x["quantity"]) > 0.0, client.get(stock_positions())['results']))}
        return pd.DataFrame([{**v,**{'symbol':k, 'equity': cls.fetch_price(client,k)* float(v['quantity'])}} for k, v in positions.items()]) if positions else pd.DataFrame([{'equity':0}])
    
    @classmethod
    def fetch_all_option_orders(cls, client):
        return client.get(option_orders())['results']

    @classmethod
    def fetch_option_order_by_id(cls, client, id):
        return client.get(option_order(id))
    
    @classmethod
    def fetch_stock_order_by_id(cls, client, id):
        return client.get(stock_order(id))
    
    @classmethod
    def fetch_all_stock_orders(cls, client):
        return client.get(stock_orders())['results']
    
    @classmethod
    def submit_option_order(cls, client, direction, legs, price, quantity, time_in_force='gfd', trigger='immediate', order_type='limit'):
        # direction = credit/debit
        payload = {'account': account(client.account_id), 'direction': direction, 'legs': legs, 'price': str(price), 'quantity': int(quantity), 'time_in_force': time_in_force, 'trigger': trigger, 'type': order_type, 'override_day_trade_checks': False, 'override_dtbp_checks': False, 'ref_id': str(uuid.uuid4())}
        return client.post(option_orders(), payload=payload)
    
    @classmethod
    def cancel_option_order(cls, client, cancel_url):
        return True if client.post(cancel_url) == {} else False

    @classmethod
    def replace_option_order(cls, client, option_order, new_price):
        result = cls.cancel(client, option_order['cancel_url'])
        if result:
            payload = json.dumps({'account': account(client.account_id), 'direction': option_order['direction'], 'legs': option_order['legs'], 'price': new_price, 'quantity': option_order['quantity'], 'time_in_force': option_order['time_in_force'], 'trigger': option_order['trigger'], 'type': option_order['type'], 'override_day_trade_checks': False, 'override_dtbp_checks': False, 'ref_id': str(uuid.uuid4())})
            return client.post(option_orders(), payload=payload)
        return False

    @classmethod
    def submit_stock_order(cls, client, symbol, quantity, side, price=None, time_in_force='gfd', trigger='immediate', order_type='market'):
        s = client.get(stock(symbol.upper()))['results'][0]
        payload = {'account': account(client.account_id),'instrument': s['url'],'quantity': int(quantity),'side': side.lower(),'symbol': symbol.upper(),'time_in_force': time_in_force.lower(),'trigger': trigger.lower(),'type': order_type.lower()}
        if order_type.lower() == "stop":
            payload['stop_price'] = float(client.get(s['quote'])['bid_price']) if not price else float(price)
        else:
            payload['price'] = float(client.get(s['quote'])['bid_price']) if not price else float(price)
        return client.post(stock_orders(),payload=payload)
    
    @classmethod
    def cancel_stock_order(cls, client, cancel_url):
        return True if client.post(cancel_url) == {} else False
