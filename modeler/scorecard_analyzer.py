import pandas as pd
from firebase import Firebase

class ScorecardAnalyzer:
    
    METRICS = ['momentum','overlays','other','score','weighted_score']

    def __init__(self, df, metric=None, threshold=0.8):
        self.df = self.get_metric_probabilities(df, metric) if metric else self.get_probabilities(df,threshold)
    
    def get_probabilities(self, df, threshold):
        df = pd.DataFrame(columns=['metric','metric_score','pct_correct']).append([self.get_metric_probabilities(df, metric) for metric in self.METRICS],ignore_index=True)
        return df[df['pct_correct'] > threshold].sort_values(by=['pct_correct'], ascending=False)
    
    def get_metric_probabilities(self, df, metric):
        return pd.DataFrame([{'metric':metric, 'metric_score':s, 'pct_correct': df[df[metric] == s]['up'].sum() /df[df[metric] == s].shape[0]} for s in list(df[metric].unique())])[['metric','metric_score','pct_correct']]

df = Firebase().get('scorecard/AMD_scorecard_10.csv')
sc = ScorecardAnalyzer(df)
print(sc.df)