import pandas as pd
from functools import wraps
from collections import ChainMap
try:
    from iex.base import IEXClient
except:
    from .iex.base import IEXClient

##################################### WRAPPERS ##################################################
def verify_fundamentals_exist(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if ('fundamentals_df') not in dir(self):
            self.fundamentals_df = load_file(self, 'fundamentals','fundamentals')
        return func(self, *args, **kwargs)
    return wrapper

class StockProfile(IEXClient):
    def __init__(self, *args, **kwargs):
        IEXClient.__init__(self, args[0])
        self.data = getattr(self, args[1])()

    def company_data(self, endpoints=['peers','company','key_stats']):
        return dict(ChainMap(*[getattr(self, 'get_%s'%ep)() for ep in endpoints]))
    
    @verify_fundamentals_exist
    def profitablility(self, span='ttm'):
        """A method for calculating profitability metrics from the fundamentals df
        Parameters
        ----------
        span : str, optional
            the span to compute the profitability metrics for, options are 'ttm' and 'mrq', (default is 'ttm')
        Returns
        -------
        dict
            a dictionary of the profitability metrics
        """
        df = self.fundamentals_df.head(5) if span == 'ttm' else self.fundamentals_df.head(2)
        return {k: round(100*v,2) for k, v in {'grossProfitMargin':(df['totalRevenue'].sum()-df['costOfRevenue'].sum())/df['totalRevenue'].sum(), 'operatingProfitMargin':df['ebit'].sum()/df['totalRevenue'].sum(), 'netProfitMargin':df['operatingIncome'].sum()/df['totalRevenue'].sum()}.items()}
    
    @verify_fundamentals_exist
    def growth(self, comparison='qoq'):
        """A method for calculating growth rates from the fundamentals df
        Parameters
        ----------
        comparison : str, optional
            the time period comparison to calculate growth rates for, options are 'qoq','yoy', default is ('yoy')
        Returns
        -------
        dict
            a dictionary of the growth rates
        """
        df = self.fundamentals_df.head(2) if comparison == 'yoy' else self.fundamentals_df.head(5)
        return {'epsGrowthQoQ': df.loc[0,'actualEPS']/df.loc[1,'actualEPS'],'revGrowthQoQ': round(100*((df.loc[0,'totalRevenue']/df.loc[1,'totalRevenue']) -1),2)} if comparison == 'qoq' else {'epsGrowthYoY': df.loc[0,'yearAgoChangePercent'],'revGrowthYoY':round(100*(df.loc[0,'totalRevenue']/df.loc[list(df.index)[-1],'totalRevenue'])-1,2)}
    
    @verify_fundamentals_exist
    def effectiveness(self):
        df = self.fundamentals_df.head(5)
        return {k: round(100*v,2) for k,v in {'ROE': df['netIncome'].sum()/df.loc[0,'shareholderEquity'], 'ROA': df['netIncome'].sum()/df['totalAssets'].mean()}.items()}

    @verify_fundamentals_exist
    def financial_strength(self):
        return {'quickRatio': round((self.fundamentals_df.loc[0,'currentAssets'] - self.fundamentals_df.loc[0,'inventory'])/self.fundamentals_df.loc[0,'totalCurrentLiabilities'],2), 'debtToCapital': round(100*(self.fundamentals_df.loc[0,'totalDebt']/(self.fundamentals_df.loc[0,'totalDebt'] + self.fundamentals_df.loc[0,'shareholderEquity'])),2)}

    def valuation(self):
        return {k:v for k, v in self.get_advanced_stats().items() if k in self.fields['valuation']}

    def ratios(self):
        return {**self.valuation(), **self.financial_strength(), **self.effectiveness(), **self.growth(), **self.growth('yoy'),**self.profitablility()}


#Costs appx. 175,000 messages to add all artifacts
