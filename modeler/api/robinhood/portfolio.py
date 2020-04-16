import time
import pandas as pd
try:
    from client import Client
    from client_methods import ClientMethods
    from chain import Chain
    from util import dte, black_scholes
    from wrappers import filter_option_orders, filter_stock_orders, filter_options_positions
except:
    from .client import Client
    from .client_methods import ClientMethods
    from .chain import Chain
    from .util import dte, black_scholes
    from .wrappers import filter_option_orders, filter_stock_orders, filter_options_positions


class Portfolio:
    def __init__(self):
        self.client = Client()
    
    def account(self):
        return ClientMethods.fetch_account(self.client)

    def portfolio(self):
        return ClientMethods.fetch_portfolio(self.client)

    def equity(self):
        return self.portfolio()['equity']
    
    def market_value(self):
        return self.portfolio()['market_value']
    
    def cash(self):
        return self.account()['portfolio_cash']

    @filter_option_orders
    def get_option_orders(self, **kwargs):
        """A method to get the option orders based on their state
        Parameters
        ----------
        state : str, optional
            the state of the option order, default is ('confirmed'), others are 'unconfirmed','filled','cancelled', None. If None, will ignore the state
        opening_strategy : str, optional
            the strategy of the order to get, if None, will ignore the opening_strategy, (default is None), others are 'iron_condor'
        symbol : str, optional
            the symbol to get orders for, works along with other params, (default is None), if None, will ignore
        ids : bool, optional
            if True, will return the option ids for the resulting orders (default is False)
        Returns
        -------
        list
            a list of dictionaries, where each dictionary is an order
        """
        return list(ClientMethods.fetch_all_option_orders(self.client))

    @filter_stock_orders
    def get_stock_orders(self, **kwargs):
        """A method to get the stock orders based on their params
        Parameters
        ----------
        state : str, optional
            the state of the stock order, default is ('confirmed'), others are 'unconfirmed','filled','cancelled', None. If None, will ignore the state
        type : str, optional
            the type order to get, if None, will ignore the type, (default is None), options are: 'limit','market'
        symbol : str, optional
            the symbol to get orders for, works along with other params, (default is None), if None, will ignore
        ids : bool, optional
            if True, will return the stock order ids for the resulting orders (default is False)
        Returns
        -------
        list
            a list of dictionaries, where each dictionary is an order
        """
        return ClientMethods.fetch_all_stock_orders(self.client)

    def get_option_leg(self, symbol, expiration, strike, type, side, position_effect, ratio_quantity=1):
        """A method for getting the formatted option leg for placing an order.
        Parameters
        ----------
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
        Returns
        -------
        list
            a list of dictionaries with the data needed for the order to be placed
        """
        chain = Chain(symbol)
        return [{'option': chain.get_option_url(strike, expiration, type), 'side': side, 'position_effect': position_effect, 'ratio_quantity': ratio_quantity}]
    
    @filter_options_positions
    def get_option_positions(self, **kwargs):
        """A method for getting current option positions
        Parameters
        ----------
        symbol : str, optional
            the symbol to get positions for
        type : str, optional
            the type of position (options are 'short','long')
        ids : bool, optional
            if True, will return the option ids for the requested position (default is False)
        Returns
        -------
        list
            a list of dictionaries with info on the option positions
        """
        return ClientMethods.fetch_option_positions(self.client)

    def get_theoretical_mark_of_positions(self):
        data = [ClientMethods.fetch_by_id(self.client,id) for id in self.get_option_positions(ids=True)]
        prices = {sym: ClientMethods.fetch_price(self.client, sym) for sym in list(pd.DataFrame(data)['chain_symbol'].unique())}
        for option in data:
            option['theoretical_mark'] = black_scholes(prices[option['chain_symbol']],float(option['strike_price']), dte(option['expiration_date'])/365,.0094,float(option['implied_volatility']), option['type'])
        return pd.DataFrame(data)[['chain_symbol','strike_price','expiration_date','theoretical_mark','mark_price','volume','open_interest']]
