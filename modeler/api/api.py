import os, time
import pandas as pd
from datetime import datetime
try:
    from historicals import Historicals
    from artifacts import Artifacts
    from profile import StockProfile
    from measurements import ChainMeasurements
    from timeseries_archive import TimeSeriesArchive
    from scorecard import Scorecard
    from scorecard_analyzer import ScorecardAnalyzer
    from util import convert_timestamp, number_timestamps
except:
    from .historicals import Historicals
    from .artifacts import Artifacts
    from .profile import StockProfile
    from .measurements import ChainMeasurements
    from .timeseries_archive import TimeSeriesArchive
    from .scorecard import Scorecard
    from .scorecard_analyzer import ScorecardAnalyzer
    from .util import convert_timestamp, number_timestamps

artifacts = ['fundamentals', 'analyst', 'insider_summary', 'insider_roster', 'insider_transactions', 'fund_ownership', 'institutional_ownership', 'dividends']

##################################### WRAPPERS ##################################################
def get_record(records):
    return pd.DataFrame([{'date':records.iloc[0,0],'minute':records.iloc[0,1],'open':records.iloc[0,2], 'high': records['high'].max(), 'low': records['low'].min(), 'close': records.iloc[-1,5], 'volume': records['volume'].sum()}])

def finish_blob(func):
    def wrapper(self):
        data = func(self)
        data['uri'] = ''.join([data['root'],'/','_'.join([self.symbol,data['root'],data['descriptor']] if data['descriptor'] else [self.symbol,data['root']]), '.csv'])
        return data
    return wrapper

def finish_document(func):
    def wrapper(self):
        return {'data': func(self), 'collection': self.kwargs['collection'], 'key': self.symbol}
    return wrapper

class API:
    def __init__(self, *args, **kwargs):
        self.symbol, self.task, self.args, self.kwargs = args[0].upper(), args[1], args[2:], kwargs
        self.input = args[2] if isinstance(args[2],pd.DataFrame) else (None if len(self.args[0]) == 0 else (self.args[0][0] if isinstance(self.args[0][0],pd.DataFrame) else None))
        self.outputs = self.start_task()

    def start_task(self):
        return self.average_periodic_volume() if self.task == 'average_volume' else (self.intraday_historicals() if self.task == 'intraday_historicals' else (self.document_task() if self.task == 'company_data' else (self.archive_dynamic() if self.task == 'archive_dynamic' else self.blob_task())))

    @finish_blob
    def blob_task(self):
        obj = ChainMeasurements(self.symbol, input=self.input, interval=self.kwargs.get('interval'), dummy=self.kwargs.get('dummy')) if self.task == 'options' else (Historicals(self.symbol, **{**self.kwargs,**{'input':self.input}}) if self.task == 'historicals' else (TimeSeriesArchive(self.symbol, self.input) if self.task == 'archive_timeseries' else (Scorecard(self.input, self.kwargs.get('interval'), **self.kwargs) if self.task == 'scorecard' else (ScorecardAnalyzer(self.input, self.kwargs.get('interval'), **self.kwargs) if self.task == 'score' else Artifacts(self.symbol, self.task, input=self.input)))))
        return obj.data
    
    @finish_document
    def document_task(self):
        obj = StockProfile(self.symbol, self.task)
        return obj.data
    
    def intraday_historicals(self):            
        h = Historicals(self.symbol, interval='dynamic')
        records = h.data['df']
        dfs = [{'df':records,'uri': 'historicals/' + '_'.join([self.symbol, 'historicals','dynamic']) + '.csv'}]
        for i in range(len(self.args[0])):
            for record in self.args[0][i]:
                for uri, df in record.items():
                    interval = int(uri.split('/')[-1].split('.')[0].split('_')[-1])
                    df = df[df['date'] != list(records['date'].unique())[0]]
                    for i in range(int(records.shape[0]/interval)):
                        df = df.append(get_record(records[i*interval:(1+i)*interval]),sort=False,ignore_index=True)
                    df['change'] = [0] + [df.iloc[i,5] - df.iloc[i-1,5] for i in range(1, df.shape[0])]
                    df['changePercent'] = [0] + [round(100*(df.iloc[i,7] / df.iloc[i-1,5]),2) for i in range(1, df.shape[0])]
                    dfs.append({'df': df, 'uri': uri})
        return dfs
    
    def archive_dynamic(self):
        df = number_timestamps(list(self.args[0][0][0].values())[0])
        df = pd.DataFrame([{**{'time_stamp': ts, 'implied_volatility': df[df['time_stamp'] == ts]['implied_volatility'].mean()}, **{t+'_'+m:df[(df['time_stamp'] == ts) & (df['type'] == t)][m].sum() for t in ['call', 'put'] for m in ['volume','open_interest']}} for ts in list(df['time_stamp'].unique())])
        df['date'] = df['time_stamp'].apply(lambda x: x.split('_')[0])
        if not isinstance(list(self.args[0][0][1].values())[0],pd.DataFrame):
            return [{'df': df, 'uri': list(self.args[0][0][1].keys())[0]}, {'df': ChainMeasurements(self.symbol, input=None, interval='dynamic', dummy=True).df, 'uri': list(self.args[0][0][0].keys())[0]}]
        return [{'df': list(self.args[0][0][1].values())[0].append(df,sort=False,ignore_index=True), 'uri': list(self.args[0][0][1].keys())[0]}, {'df': ChainMeasurements(self.symbol, input=None, interval='dynamic', dummy=True).df, 'uri': list(self.args[0][0][0].keys())[0]}]

    def average_periodic_volume(self):
        return {'df': pd.DataFrame([{'minute':m, 'v10': self.input[(self.input['minute'] == m)]['volume'].mean()} for m in list(self.input['minute'].unique())]) if self.kwargs['interval'] in ['10','30'] else pd.DataFrame([self.input['date'],pd.Series(data=self.input['volume'].rolling(window=10, min_periods=10).mean(),name='v10')]).T, 'uri': 'averages/{}_averages_{}.csv'.format(self.symbol, self.kwargs['interval'])}
