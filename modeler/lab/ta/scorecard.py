import time
import pandas as pd
from technicals import Technicals
from unsupervised import AssociationRules

def cut(series, n=10):
    return pd.qcut(series,n,labels=False,retbins=False,duplicates='drop')

class Scorecard:
    def __init__(self, df, ntiles=None):
        self.df = df
        self.sc = Technicals(df, change_only=True, ntiles=ntiles).df
        self.filters = [('con', "x == ['up'] or x == ['down']"),('ant_len', "x == 1")]
        self.indicator_buckets = [('momentum',['rsi','wr','stoch_k','stoch_d','tsi','ao','mfi','uo']),('other',['macd','trix','cci','aroon','kst','bb','kc','cmf'])]
    
    def scorecard(self):
        sc = self.sc.join([self.indicator_scorecard(),self.overlay_scorecard()])
        sc['momentum'], sc['other'], sc['overlays'] = cut(sc['momentum']), cut(sc['other']), cut(sc['overlays'])
        sc['score'] = sc.iloc[:,self.sc.shape[1]:].sum(axis=1)
        mm_wts = {v:sc[sc['momentum'] == v]['up'].sum() / sc[sc['momentum'] == v].shape[0] for v in list(sc['momentum'].unique())}
        oth_wts = {v:sc[sc['other'] == v]['up'].sum() / sc[sc['other'] == v].shape[0] for v in list(sc['other'].unique())}
        ovl_wts = {v:sc[sc['overlays'] == v]['up'].sum() / sc[sc['overlays'] == v].shape[0] for v in list(sc['overlays'].unique())}
        sc['weighted_score'] = cut(pd.DataFrame([sc['momentum'].apply(lambda x: mm_wts[x]), sc['other'].apply(lambda x: oth_wts[x]), sc['overlays'].apply(lambda x: ovl_wts[x])]).T.sum(axis=1),11)
        return sc

    def indicator_scorecard(self):
        return pd.DataFrame([pd.Series(self.sc.join([self.score_indicator(ind) for ind in bucket[1]]).iloc[:,self.sc.shape[1]:].fillna(0).sum(axis=1),name=bucket[0]) for bucket in self.indicator_buckets]).T

    def overlay_scorecard(self):
        return pd.Series(self.sc.join([self.score_overlay(ovl,per) for ovl in ['ema','sma'] for per in [10, 20, 30, 50, 100, 200]]).fillna(0).iloc[:,self.sc.shape[1]:].sum(axis=1),name='overlays')
        
    def score_indicator(self, ind):
        df = Technicals(self.df, overlays=False, indicators=[ind.upper()]).df
        ar = AssociationRules(df, min_sup=0, min_thresh=0, filters=self.filters).df.fillna(0)
        ar['ant'], ar['con'] = ar['ant'].apply(lambda x: x[0]), ar['con'].apply(lambda x: x[0])
        buy = ar.loc[ar[(ar['ant'] == ind+'_buy') & (ar['con'] == 'up')].index.tolist()[0],'conf'] - ar.loc[ar[(ar['ant'] == ind+'_buy') & (ar['con'] == 'down')].index.tolist()[0],'conf']
        sell = ar.loc[ar[(ar['ant'] == ind+'_sell') & (ar['con'] == 'up')].index.tolist()[0],'conf'] - ar.loc[ar[(ar['ant'] == ind+'_sell') & (ar['con'] == 'down')].index.tolist()[0],'conf']
        df[ind+'_buy'], df[ind+'_sell'] = df[ind+'_buy'].apply(lambda x: buy if x == 1 else 0),df[ind+'_sell'].apply(lambda x: buy if x == 1 else 0)
        return df.iloc[:,-2:]
    
    def score_overlay(self, ovl, per):
        df = Technicals(self.df, overlays=[ovl.upper()], overlay_periods=[per], indicators=False).df
        ar = AssociationRules(df, min_sup=0, min_thresh=0, filters=self.filters).df.fillna(0)
        ar['ant'], ar['con'] = ar['ant'].apply(lambda x: x[0]), ar['con'].apply(lambda x: x[0])
        inf_up = ar.loc[ar[(ar['ant'] == '_'.join([ovl,str(per), 'inflx','up'])) & (ar['con'] == 'up')].index.tolist()[0],'conf'] - ar.loc[ar[(ar['ant'] == '_'.join([ovl,str(per), 'inflx','up'])) & (ar['con'] == 'down')].index.tolist()[0],'conf']
        inf_down = ar.loc[ar[(ar['ant'] == '_'.join([ovl,str(per), 'inflx','down'])) & (ar['con'] == 'up')].index.tolist()[0],'conf'] - ar.loc[ar[(ar['ant'] == '_'.join([ovl,str(per), 'inflx','down'])) & (ar['con'] == 'down')].index.tolist()[0],'conf']
        dir_up = ar.loc[ar[(ar['ant'] == '_'.join([ovl,str(per), 'dx','up'])) & (ar['con'] == 'up')].index.tolist()[0],'conf'] - ar.loc[ar[(ar['ant'] == '_'.join([ovl,str(per), 'dx','up'])) & (ar['con'] == 'down')].index.tolist()[0],'conf']
        dir_down = ar.loc[ar[(ar['ant'] == '_'.join([ovl,str(per), 'dx','down'])) & (ar['con'] == 'up')].index.tolist()[0],'conf'] - ar.loc[ar[(ar['ant'] == '_'.join([ovl,str(per), 'dx','down'])) & (ar['con'] == 'down')].index.tolist()[0],'conf']
        df['_'.join([ovl,str(per), 'inflx','up'])] = df['_'.join([ovl,str(per), 'inflx','up'])].apply(lambda x: inf_up if x == 1 else 0)
        df['_'.join([ovl,str(per), 'inflx','down'])] = df['_'.join([ovl,str(per), 'inflx','down'])].apply(lambda x: inf_down if x == 1 else 0)
        df['_'.join([ovl,str(per), 'dx','up'])] = df['_'.join([ovl,str(per), 'dx','up'])].apply(lambda x: dir_up if x == 1 else 0)
        df['_'.join([ovl,str(per), 'dx','down'])] = df['_'.join([ovl,str(per), 'dx','down'])].apply(lambda x: dir_down if x == 1 else 0)
        return df.iloc[:,-4:]





st = time.time()
#df = pd.read_csv('AMD_minute_monthly.csv')
df = pd.read_csv('storage\\historicals\\AMD_daily_historicals.csv')
sc = Scorecard(df)
print(sc.scorecard())
#sc.scorecard().to_csv('test_scorecard_minute_monthly_weighted.csv',index=False)
print(time.time() - st)
