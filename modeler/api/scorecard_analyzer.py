import random
import pandas as pd

def finish(func):
    def wrapper(self):
        df = func(self)[self.DATA_COLUMNS]
        df['pct_correct'], df['delta_pct'], df['probability'] = df['pct_correct'].apply(lambda x: round(x,3)),df['delta_pct'].apply(lambda x: round(x,3)),(df['pct_correct']*df['delta_pct']).apply(lambda x:round(x,3))
        self.df = calculated_move(self, df).sort_values(by=['pct_correct','calc_move'], ascending=False)
        return {'root': self.root, 'descriptor': self.descriptor, 'df': self.df}
    return wrapper

def calculated_move(self, df):
    ranges = sorted([0]+list(df['ntile_val'].unique()))
    ntile_ranges = {i+1: [ranges[i],ranges[i+1]] for i in range(len(self.nt_cols))}
    em = {k: round(sum([random.uniform(v[0],v[1]) for i in range(1000)])/1000,2) for k, v in ntile_ranges.items()}
    df['expected_move'] = df['ntile'].apply(lambda x: em[int(x)])
    return pd.DataFrame([{'metric': m, 'metric_score': ms, 'direction': dx, 'pct_correct':list(df[(df['metric'] == m) & (df['metric_score'] == ms) & (df['direction'] == dx)]['pct_correct'].unique())[0], 'calc_move': round(sum(df[(df['metric'] == m) & (df['metric_score'] == ms) & (df['direction'] == dx)]['probability'] * df[(df['metric'] == m) & (df['metric_score'] == ms) & (df['direction'] == dx)]['expected_move']),2)} for m in self.METRICS for ms in list(df[df['metric']==m]['metric_score'].unique()) for dx in ['up','down']])[['metric','metric_score','direction','pct_correct','calc_move']]
    
class ScorecardAnalyzer:
    
    METRICS, COLUMNS = ['momentum','overlays','other','score','weighted_score'], ['metric','metric_score','direction','pct_correct']
    NTILE_COLUMNS, DATA_COLUMNS = ['metric','metric_score','ntile','delta_pct','ntile_val'], ['metric','metric_score','direction','ntile','pct_correct','delta_pct','ntile_val']

    def __init__(self, *args, **kwargs):
        self.df, self.descriptor, self.range, self.root = args[0], args[1], args[0].shape[1] - 15 if args[1] != 'daily' else args[0].shape[1] - 14, 'scores'
        self.nt_cols = list(args[0].iloc[:,10:9+self.range] if args[1] == 'daily' else args[0].iloc[:,11:10+self.range].columns)
        self.data = self.get_data()
    
    @finish
    def get_data(self):
        return pd.merge(self.get_probabilities(),self.get_ntile_probabilities(), on=['metric','metric_score'])

    def get_probabilities(self):
        return pd.DataFrame(columns=self.COLUMNS).append([self.get_metric_probabilities(self.df, metric) for metric in self.METRICS],ignore_index=True)
    
    def get_ntile_probabilities(self):
        return pd.DataFrame(pd.DataFrame(columns=self.NTILE_COLUMNS).append([self.get_ntile_metric_probabilities(self.df, metric) for metric in self.METRICS],ignore_index=True)[self.NTILE_COLUMNS])

    def get_metric_probabilities(self, df, metric):
        return pd.DataFrame([{'metric':metric, 'metric_score':s, 'direction': dx, 'pct_correct': df[df[metric] == s][dx].sum() /df[df[metric] == s].shape[0]} for dx in ['up','down'] for s in list(df[metric].unique())])[self.COLUMNS]

    def get_ntile_metric_probabilities(self, df, metric):
        return pd.DataFrame([{'metric': metric, 'metric_score':s, 'ntile': col.split('_')[2], 'delta_pct': df[df[metric] == s][col].sum()/df[df[metric] == s].shape[0], 'ntile_val': float(col.split('_')[-1])} for col in self.nt_cols for s in list(df[metric].unique())])[self.NTILE_COLUMNS]

#df = pd.read_csv('AMD_scoredcard_ntiles_daily.csv')
#sa = ScorecardAnalyzer(df, 'daily')
#sa.df.to_csv('AMD_scores_daily.csv', index=False)
