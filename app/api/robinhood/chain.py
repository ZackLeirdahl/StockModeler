
import json, time
import pandas as pd
from queue import Queue
from threading import Thread
from dateutil.parser import parse
try:
    from client_methods import ClientMethods
    from client import Client
    from endpoints import stock, option_chain
    from util import dte, black_scholes, format_strike
    from wrappers import populate_queue, append_fields, latest_price, filter_fields
except:
    from .client_methods import ClientMethods
    from .client import Client
    from .endpoints import stock, option_chain
    from .util import dte, black_scholes, format_strike
    from .wrappers import populate_queue, append_fields, latest_price, filter_fields

class Chain:
    def __init__(self, symbol, populate=True):
        self.symbol, self.client = symbol.upper(), Client()
        self.stock_id = self.client.get(stock(self.symbol))['results'][0]['id']
        self.options = self.build_chain() if populate else None
            
    @append_fields
    def build_chain(self):
        self.q = Queue(maxsize=0)
        self.initialize_chain()
        self.thread_factory()
        self.q.join()
        return pd.concat(self.dfs) if self.dfs else None

    @latest_price
    @populate_queue
    def initialize_chain(self):
        return self.client.get(option_chain(), params={'equity_instrument_ids':self.stock_id})['results'][-1]
    
    def thread_factory(self):
        for thread in [Thread(target=self.process_q) for i in range(self.num_threads)]:
            thread.daemon = True
            thread.start()

    def process_q(self):
        while not self.q.empty():
            self.dfs.append(ClientMethods.fetch_by_expiration(self.client, self.id, [self.q.get()]))
            self.q.task_done()

    def get_option(self, expiration, strike,  type):
        """A method to get a single option from the chain.
        Parameters
        ----------
        expiration : str
            the expiration of the option
        strike : str, float, int
            the strike price of the option
        type : str
            the type of option ('call','put')
        Returns
        -------
        dict
            the dictionary data of the option
        """
        return self.options[(self.options['type'] == type) & (self.options['strike_price'] == format_strike(str(strike))) & (self.options['expiration_date'] == parse(expiration).strftime('%Y-%m-%d'))].to_dict('records')[0]

    @filter_fields
    def get_active_options(self, expiration=None, measure='volume', option_type='call', limit=1):
        """A method to get the most active options based on the parameters.
        Parameters
        ----------
        expiration : str, optional
            if a valid expiration date, will return the most active option for that expiration(s), if None will return the most active option(s) for the entire chain (default is None)
            str --> valid date string
        measure : str, optional
            the measure of activity to find the most active, possible values are 'volume' and 'open_interest', (default is 'volume')
        option_type : str, optional
            the type of option to get, acceptable values are 'call' and 'put' (default value is 'call')
        limit : int, optional
            the top n amount of options to return, (default is 1)
        Returns
        -------
        DataFrame
            a DataFrame of the option data for the most active option(s)
        """
        return self.options[self.options['type'] == option_type].sort_values(by=[measure], axis=0, ascending=False).head(limit) if expiration is None else self.options[(self.options['type'] == option_type) & (self.options['expiration_date'] == parse(expiration).strftime('%Y-%m-%d'))].sort_values(by=[measure], axis=0, ascending=False).head(limit)
    
    @latest_price
    def get_options_with_limit(self, expirations=None, limit=12):
        """
        A method to filter the option chain by type, expiration date and proximity to current stock price.
        Parameters
        ----------
        type : str, optional
            The type of option to get, acceptable values are 'call' and 'put' (default value is 'call')
        expirations : int, optional
            The amount of expirations to look at (default value is None), if value is None, will get all expirations
        limit : int, optional
            The amount of option strikes to return that match the type and expriations criteria (default value is 12)
        Returns
        -------
        list
            sorted list of options that match the type, expirations and limit criteria.
        """
        options = self.options[(self.options['expiration_date'].isin(self.expiration_dates[:expirations]))] 
        return options[(options['strike_price'].isin([strike[0] for strike in sorted({strike: abs(float(strike) - self.price) for strike in options['strike_price'].unique()}.items(),key=lambda x: x[1])[:limit]]))]
    
    @latest_price
    def get_max_pain(self, expirations=1):
        """
        A method to get the max pain points for the provided symbol, by expiration date.
        Parameters
        ----------
        expirations : int, optional
            The amount of expirations to look at (default value is 1)
        Returns
        -------
        pandas.DataFrame
            A DataFrame of the expiration date, strike price and total value of the max pain points for the expirations provided
        """
        options = self.get_options_with_limit(expirations=expirations)
        chain = {exp: dict.fromkeys(options['strike_price'].unique(),{}) for exp in self.expiration_dates[:expirations]}
        for option in options.to_dict('records'):
            chain[option['expiration_date']][option['strike_price']][option['type']] = option['open_interest']
        return pd.DataFrame({k: min({kk: 100 * round(sum([(self.price - float(kk)) * vv['call'] if self.price > float(kk) else (float(kk) - self.price) * vv['put']]),2)}.items(), key=lambda x: x[1]) for k, v in chain.items() for kk, vv in v.items()}).transpose().set_axis(['strike', 'value'], axis='columns', inplace=False)
    
    def get_average_implied_volatility(self):
        """
        A method to get the average implied volatility for the option chain of the provided symbol.
        Returns
        -------
        float
            the average implied volatilty for the option chain
        """
        return round(self.get_options_with_limit()['implied_volatility'].astype('float64').mean(),4)

    def get_liquid_options(self, type='call',limit=10):
        """ A method to get the most liquid options in the chain.
        Parameters
        ----------
        type : str, optional
            the type of option, default is 'call'
        limit : int, optional
            the number of options to return, default is 10
        Returns
        -------
        pandas.DataFrame
            a dataframe of the most liquid options
        """
        return self.options[self.options['type']==type].sort_values(by=['volume','vol_oi_ratio','bid_ask_spread'], ascending=[False,False,True]).head(limit)

    def get_option_spread(self):
        """ A method to get the spread for the option chain
        Returns
        -------
        pandas.DataFrame
            A DataFrame of the spread information
        """
        data = {**{k + '_' + measure: v  for measure in ['volume','open_interest'] for k, v in self.options.groupby(['type'])[measure].sum().to_dict().items()},**{measure: self.options[measure].sum() for measure in ['volume','open_interest']}}
        data['call_put_ratio'] = round(data['call_volume']/data['put_volume'],3)
        return pd.DataFrame([data])

    def get_theoretical_mark(self, strike, exp, type = 'call'):
        """ A method to get the theoretical mark price for an option.
        Parameters
        ----------
        strike : float, int, str
            the strike price of the option
        exp : str
            the expiration for the option
        type : str, optional
            the option type, 'call' or 'put', default is 'call'
        Returns
        -------
        float
            the theoretical mark price
        """
        return black_scholes(float(self.price), float(strike), dte(exp)/365, .0094, float(self.options[(self.options['type'] == type) & (self.options['strike_price'] == str(strike) + '.0000' if len(str(strike).split('.')) == 1 else str(strike) + '000') & (self.options['expiration_date'] == parse(exp).strftime('%Y-%m-%d'))].to_dict('records')[0]['implied_volatility']), type)

""" TO DO
- create a method to get highest volume - open interest ratio
    - volume must meet a threshold
"""
