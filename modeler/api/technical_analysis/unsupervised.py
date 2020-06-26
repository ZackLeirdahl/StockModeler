import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
try:
    from technicals import Technicals
except:
    from .technicals import Technicals

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
