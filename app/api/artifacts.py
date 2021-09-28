
import pandas as pd
from datetime import datetime
from functools import reduce
from .iex.base import IEXClient
from .util import time_ordinal

##################################### WRAPPERS ##################################################
def clean_artifact(func):
    def wrapper(self, artifact):
        df = func(self, artifact)
        if artifact in ['dividends','fundamentals']:
            df = df.drop_duplicates(subset='declaredDate' if artifact == 'dividends' else 'reportDate',keep='last')
        if artifact in ['fund_ownership','institutional_ownership','insider_roster']:
            df['reportDate'] = df['reportDate'].apply(lambda x: datetime.fromtimestamp(x/1000.0).strftime('%Y-%m-%d'))
            df = df.sort_values(by='reportDate')
        self.df = df
        return {'root': self.root, 'descriptor': self.descriptor, 'df': self.df}
    return wrapper

class Artifacts(IEXClient):
    def __init__(self, *args, **kwargs):
        """
        symbol : str
            the symbol to retrieve artifacts for
        artifact : str
            the name of the artifact to retrieve (see iex.base)
        input : pd.DataFrame, optional
            an input df to append results to
        """
        IEXClient.__init__(self, args[0])
        self.root = args[1] if len(args[1].split('_')) < 2 else (args[1].split('_')[0] if args[1].split('_')[0] == 'insider' else args[1].split('_')[-1])
        self.descriptor = '' if len(args[1].split('_')) < 2 else (args[1].split('_')[-1] if args[1].split('_')[0] == 'insider' else args[1].split('_')[0])
        self.df = kwargs.get('input')
        self.data = self.get_artifact(args[1])

    @clean_artifact
    def get_artifact(self, artifact):
        if artifact == 'fundamentals':
            return reduce(lambda x, y: pd.merge(x,y, on='reportDate',how='left'),[getattr(self, 'get_%s' % ep)(last=12) for ep in ['income_statement','financials','cash_flow','earnings','balance_sheet']]) if self.df is None else (pd.concat([reduce(lambda x,y: pd.merge(x,y,on='reportDate',how='left'), [getattr(self, 'get_%s' % ep)() for ep in ['income_statement','financials','cash_flow','earnings','balance_sheet']]),self.df]))
        if artifact == 'analyst':
            return pd.DataFrame([{**{'dataDate':time_ordinal()},**{k:v for k,v in {**self.get_price_target(), **self.get_recommendation_trends(), **self.get_estimates()}.items() if k in self.FIELDS['analyst']}}]) if self.df is None else pd.concat([pd.DataFrame([{**{'dataDate':time_ordinal()},**{k:v for k,v in {**self.get_price_target(), **self.get_recommendation_trends(), **self.get_estimates()}.items() if k in self.FIELDS['analyst']}}]),self.df])
        if artifact == 'dividends':
            return self.get_dividends() if self.df is None else pd.concat([self.get_dividends(range='3m'),self.df])
        return getattr(self, 'get_%s' % artifact)() if self.df is None else pd.concat([getattr(self, 'get_%s' % artifact)(),self.df])
