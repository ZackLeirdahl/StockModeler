import math, time
import pandas as pd
from functools import wraps
try:
    from client_methods import ClientMethods
    from chain import Chain
    from portfolio import Portfolio
    from util import get_long_short_difference, get_max_quantity
except:
    from .client_methods import ClientMethods
    from .chain import Chain
    from .portfolio import Portfolio
    from .util import get_long_short_difference, get_max_quantity

class Order(Portfolio):
    def __init__(self, symbol=None):
        Portfolio.__init__(self)

    def _check_status(self, chain_symbol, max_retry=5):
        order = self.get_option_orders(chain_symbol=chain_symbol).to_dict('records')[0]
        return True if self.id == order['id'] and order['state'] == 'filled' else (False if max_retry == 0 else _check_status(self, chain_symbol, max_retry=max_retry-1))

    def _confirm_order(func):
        def wrapper(self, *args, **kwargs):
            order = func(self, *args, **kwargs)
            self.id, self.cancel_url = order['id'], order['cancel_url']
            self.status = self._check_status(args[0])
            return {'time': time.time() - self.elapsed, 'id': self.id, 'status': self.status}
        return wrapper

    def _set_order(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            self.elapsed, id, cash, chain = time.time(), True if len(args) == 4 else False, self.get_cash(), Chain(args[0]) if not len(args) == 4 else None
            option = chain.get_option(args[1],args[2],args[3]) if not id else ClientMethods.fetch_by_id(self.client, args[1])
            self.direction = 'debit' if args[4 if not id else 2] == 'buy' else 'credit'
            self.legs = [{'option': option['url'], 'side': args[4 if not id else 2], 'position_effect': args[5 if not id else 3], 'ratio_quantity': kwargs.get('ratio_quantity',1)}]
            self.price = option['high_fill_rate_buy_price' if args[4 if not id else 2] == 'buy' else 'high_fill_rate_sell_price'] if not kwargs.get('price') else kwargs['price'] 
            self.quantity = kwargs.get('quantity',1) if not kwargs.get('max_quantity') else (math.floor(cash/self.price) if math.floor(cash/self.price) <= kwargs['max_quantity'] else 1)
            return func(self, *args, **kwargs)
        return wrapper

    @_confirm_order
    @_set_order
    def order_option(self, *args, **kwargs):
        """ A method to place an order for an option.
        Parameters
        ----------
        symbol : str
            the stock symbol to get the option for
        expiration or id: str, int; str
            the expiration date of the option;
            the id of the option
        strike or side: str, int; str
            the strike price for the option;
            the side of the option to take ('buy','sell')
        type or position_effect: str; str
            the type of option
            the action to take on the option ('open','close')
        side : str
            the side of the option to take ('buy','sell')
        position_effect : str
            the action to take on the option ('open','close')
        """
        return ClientMethods.submit_option_order(self.client, self.direction, self.legs, self.price, self.quantity)
    
    @_confirm_order
    @_set_order
    def replace_option(self, *args, **kwargs):
        """ A method to replace an order for an option.
        Parameters
        ----------
        symbol : str
            the stock symbol to get the option for
        expiration or id: str, int; str
            the expiration date of the option;
            the id of the option
        strike or side: str, int; str
            the strike price for the option;
            the side of the option to take ('buy','sell')
        type or position_effect: str; str
            the type of option
            the action to take on the option ('open','close')
        side : str
            the side of the option to take ('buy','sell')
        position_effect : str
            the action to take on the option ('open','close')
        """
        return ClientMethods.replace_option_order(self.client, self.cancel_url, self.direction, self.legs, self.price, self.quantity)

    def close_option(self, *args, **kwargs):
        """ A method to close an already open option.
        Parameters
        ----------
        symbol : str
            the stock symbol to get the option for
        id : str
            the id of the option
        side :  str
            the side of the option to take ('buy','sell')
        position_effect :  str
            the action to take on the option ('open','close')
        """
        self.order_option(*args, **kwargs)
        while not self.status:
            self.replace_option(*args, **kwargs)
        return True

    def close_position(self, symbol):
        """ A method to close out out of all open options for a symbol.
        Parameters
        ----------
        symbol : str
            the stock symbol to get the option for
        """
        #Need to add a check for intraday_quantity, if not 0 then was bought today
        #Need to check if there are any pending orders for any options before determining quantity
        df = self.get_option_positions(symbol=symbol)
        if df.shape[0] == 0:
            return True
        exp = sorted({exp: len(list(df[df['expiration_date'] == exp]['type'].unique())) for exp in list(df['expiration_date'].unique())}.items(),key=lambda x: (x[1],x[0]))[0]
        df = df[df['expiration_date']==exp[0]].sort_values(by=['quantity','type','mark_price'], ascending=[False,False,True]) if exp[1] > 1 else df
        option = list(df['option'].unique())[0] if exp[1] > 1 else list(df[df['expiration_date']==exp[0]]['option'].unique())[0]
        self.close_option(symbol, option[:-1].split('/')[-1], 'sell' if exp[1] == 1 or get_long_short_difference(df) > 0  else 'buy', 'close', max_quantity=get_max_quantity(df, option, exp[1]))
        self.close_position(symbol)

    def order_stock(self, symbol, quantity, side, price=None):
        """ A method to place for a stock order.
        Parameters
        ----------
        symbol : str
            the stock symbol to get the place the order on
        quantity : int, str
            the amount of shares to place the order for
        side : str
            the side of the order to take ('buy','sell')
        price : float, optional
            the price to place the order at, if None, will place at the bid price
        """
        return ClientMethods.submit_stock_order(self.client, symbol, quantity, side, price=price)




#o = Order()
#print(o.close_position('CGC'))
##print(o.order_option('NOK','2020-07-24',4.5,'call','buy','open', quantity=1))
#print(o.order_option('AMD','2020-07-02',52,'put','sell','close', quantity=1))
#print(o.order_option('TLRY','2020-06-26','10.5','call','buy','close',quantity=1))
#print(o.order_option('TLRY','2020-06-26','10','call','sell','close',quantity=2))

""" TO DO
    -  create a "close positions" method

        - for each expiration:
            - check for long and short
                - if long only: close
                - if long and short:
                    - buy short then sell long
        - order:
            1) uncovered longs
            2) earliest expiration
            3) enough cash to buy the short
        - rules:
            - order the highest quantity per order
            - if more long than short for an expiration --> sell the cheapest long until even amount
            - if same amount of short and long buy the cheapest short then sell cheapest long
            
        """
