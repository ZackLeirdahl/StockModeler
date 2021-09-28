import time
import pandas as pd
try:
    from client import Client
    from client_methods import ClientMethods
    from util import dte, black_scholes
    from wrappers import filter_option_orders, filter_stock_orders, filter_options_positions, format_stock_positions
except:
    from .client import Client
    from .client_methods import ClientMethods
    from .util import dte, black_scholes
    from .wrappers import filter_option_orders, filter_stock_orders, filter_options_positions, format_stock_positions


class Portfolio:
    def __init__(self, *args, **kwargs):
        self.client = Client()
        self.data = getattr(self,'get_%s' % args[0])(**kwargs) if len(args) > 0 else None

    def get_account(self):
        return ClientMethods.fetch_account(self.client)

    def get_portfolio(self):
        return ClientMethods.fetch_portfolio(self.client)

    def get_equity(self):
        return self.get_portfolio()['equity']
    
    def get_market_value(self):
        return self.get_portfolio()['market_value']
    
    def get_cash(self):
        return float(self.get_account()['portfolio_cash'])

    def get_stock_equity(self):
        return sum(ClientMethods.fetch_stock_positions(self.client)['equity'].to_list())

    @format_stock_positions
    def get_stock_positions(self):
        return ClientMethods.fetch_stock_positions(self.client)

    @filter_option_orders
    def get_option_orders(self, **kwargs):
        """A method to get the option orders based on their state
        Parameters
        ----------
        state : str, optional
            the state of the option order, default is ('confirmed'), others are 'unconfirmed','filled','cancelled', None. If None, will ignore the state
        opening_strategy : str, optional
            the strategy of the order to get, if None, will ignore the opening_strategy, (default is None), others are 'iron_condor'
        chain_symbol : str, optional
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
        pd.DataFrame
            a data frame of the option positions that meet the parameters
        """
        return ClientMethods.fetch_option_positions(self.client)

    def get_theoretical_mark_of_positions(self, **kwargs):
        """ A method to get the theoretical mark price of current positions
        Returns
        -------
        pd.DataFrame
            a dataframe of each option and other data including the theoretical mark
        """
        positions = self.get_option_positions(ids=True)
        data = [ClientMethods.fetch_by_id(self.client,id) for id in positions['id']]
        prices = {sym: ClientMethods.fetch_price(self.client, sym) for sym in list(pd.DataFrame(data)['chain_symbol'].unique())}
        for option in data:
            option['theoretical_mark'] = black_scholes(prices[option['chain_symbol']],float(option['strike_price']), dte(option['expiration_date'])/365,.0094,float(option['implied_volatility']), option['type'])
        res = pd.merge(pd.DataFrame(data),positions, on='instrument')[['chain_symbol','strike_price','type','side','quantity','expiration_date','theoretical_mark','mark_price','volume','open_interest']]
        res['theoretical_value'] = [float(r['theoretical_mark'])*float(r['quantity']) for i, r in res.iterrows()]
        return res if not kwargs.get('symbol') else res[res['chain_symbol'] == kwargs['symbol']]

    def get_theoretical_value_of_positions(self, **kwargs):
        """ A method to get the theoretical value of each position grouped by symbol and type (call or put)
        Returns
        -------
        pd.DataFrame
            a dataframe of the theoretical value of each position
        """
        data = self.get_theoretical_mark_of_positions(**kwargs)
        res = {sym: {} for sym in list(data['chain_symbol'].unique())}
        for sym in list(data['chain_symbol'].unique()):
            for t in data[(data['chain_symbol'] == sym)]['type'].unique():
                res[sym][t] = data[(data['chain_symbol'] == sym) & (data['type'] == t)].groupby(['side'])['theoretical_value'].sum().to_dict()
        return pd.DataFrame([[k, t, tv.get('long',0) - tv.get('short',0)] for k, v in res.items() for t, tv in v.items()], columns = ['symbol','type','value'])

    def get_theoretical_value_of_portfolio(self, **kwargs):
        """ A method to get the theoretical value of the portfolio
        Returns
        -------
        float
            the theoretical value of the portfolio
        """
        return round(sum(self.get_theoretical_value_of_positions()['value'].to_list()) * 100 + self.get_cash() + self.get_stock_equity(),2)

    def get_put_call_ratio(self, **kwargs):
        """ A method to get the long and short value for the symbol and the long to short ratio
        Parameters
        ----------
        symbol : str, optional
            the symbol to get put call ratio for, if None will return for the entire portfolio
        Returns
        -------
        list
            a list of dictionaries where each is the result for the given parameters
        """
        df = pd.DataFrame(self.get_option_positions(symbol=symbol) if symbol else self.get_option_positions())
        df['mark_price'] = df['mark_price'].astype('float64')
        res = df.groupby(['type'])[['mark_price']].sum().to_dict()
        return [symbol if symbol else None,{**{k: round(v,3) for k, v in res['mark_price'].items()},**{'long_short_ratio': round(res['mark_price']['long']/res['mark_price']['short'],2)}}]

#print(Portfolio('stock_positions').data)