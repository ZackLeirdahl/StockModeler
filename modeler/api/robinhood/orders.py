import pandas as pd
from functools import wraps
try:
    from client import Client
    from client_methods import ClientMethods
    from chain import Chain
    from portfolio import Portfolio
except:
    from .client import Client
    from .client_methods import ClientMethods
    from .chain import Chain
    from .portfolio import Portfolio

def set_option(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        self.chain = Chain(args[0])
        self.option = self.chain.get_option(args[1],args[2],args[3])
        return func(self, *args, **kwargs)
    return wrapper

# def check_status(func):
#     def wrapper(self, symbol, expiration, strike, type, side, position_effect, ratio_quantity=1, quantity=1, price=None):
#         option = func(self, symbol, expiration, strike, type, side, position_effect, ratio_quantity=1, quantity=1, price=None)['legs'][0]['option']
#         options = self.get_option_positions()
        
#         return None
#     return wrapper

class Order(Portfolio):
    def __init__(self, symbol=None):
        Portfolio.__init__(self)
    
    #@check_status
    @set_option
    def order_option(self, symbol, expiration, strike, type, side, position_effect, ratio_quantity=1, quantity=1, price=None):
        """ A method to place an order for an option.
        Parameters
        ----------
        symbol : str
            the stock symbol to get the option for
        expiration : str, int
            the expiration date of the option
        strike : str, int
            the strike price for the option
        type : str
            the type of option
        side : str
            the side of the option to take ('buy','sell')
        position_effect : str
            the action to take on the option ('open','close')
        """
        direction = 'debit' if side == 'buy' else 'credit'
        legs = [{'option': self.option['url'], 'side': side, 'position_effect': position_effect, 'ratio_quantity': ratio_quantity}]
        price = price if price else self.option['high_fill_rate_buy_price' if side == 'buy' else 'high_fill_rate_sell_price']
        return ClientMethods.submit_option_order(self.client, direction, legs, price, quantity)

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
#o.order_option('NOK','2020-07-02',5,'call','buy','open', quantity=1)
#print(con)
#print(o.order_option('TLRY','2020-06-26','10.5','call','buy','close',quantity=1))
#print(o.order_option('TLRY','2020-06-26','10','call','sell','close',quantity=2))

"""
- make order
- compare return data against positions to see if order has been filled
- if it hasn't check orders to see state
- need to check quantity filled vs previous quantity if any

"""