import pandas as pd
import time
from mlxtend.frequent_patterns import apriori, association_rules
#from sklearn.tree import DecisionTreeClassifier
from technicals import Technicals

def filter(func):
    def wrapper(self, *args, **kwargs):
        df = func(self, *args, **kwargs)
        df.columns = ['ant','con','ant_sup','con_sup','sup','conf','lift','lev','conv']
        df['ant'], df['con'] = df['ant'].apply(lambda x: list(x)), df['con'].apply(lambda x: list(x))
        df['ant_len'], df['con_len'] = df['ant'].apply(lambda x: len(x)), df['con'].apply(lambda x: len(x))
        for f in self.filters:
            df = df[eval('df.{}.apply(lambda x:{})'.format(*f))]
        return df.sort_values(self.sort_by, ascending=False)
    return wrapper

class AssociationRules:
    def __init__(self, df, **kwargs):
        self.min_sup, self.min_thresh = kwargs.get('min_sup',.25), kwargs.get('min_thresh', .25)
        self.metric, self.filters, self.sort_by = kwargs.get('metric', 'support'), kwargs.get('filters',[]), kwargs.get('sort_by', 'sup')
        self.df = self.results(df)

    def results(self, df):
        return self.get_association_rules(self.get_apriori(df))

    def get_apriori(self, bin_df):
        return apriori(bin_df, min_support=self.min_sup, use_colnames=True, max_len=None)
    
    @filter
    def get_association_rules(self, apr_df):
        return association_rules(apr_df, metric=self.metric, min_threshold=self.min_thresh)


# st = time.time()
#df = pd.read_csv('storage\\historicals\\AMD_daily_historicals.csv')
#df = Technicals(df, overlays=False, indicators=['RSI'],ntiles=4, filter_cols=['rsi_nt_4','rsi_pctOfmax_nt_4']).df
#print(df.columns)
#df = Technicals(df, overlays=False).df
#ar = AssociationRules(df, min_sup=0.0, min_thresh=0.0,filters = [('con', "x == ['up'] or x == ['down']"),('ant_len', "x == 1")], sort_by='lift')

#print(ar.df)
# print(time.time() - st)

""" Algorithm parts
- predict direction --> classifications = up or down
- predict magnitude --> classifications = up/down big/small
"""

""" Classifier predictor buckets
- momentum --> use momentum indicators to create a scale of confidence (1-4? 1-10?) and categorize records
- trend
- volume
- volatility
- overlays
"""