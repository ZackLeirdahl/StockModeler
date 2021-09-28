import pandas as pd
import time, json
from datetime import datetime
try:
    from base import IEXClient
except:
    from .base import IEXClient

def add_record(self, df):
    o, h, l, c, v = df.iloc[0,0], df['latestPrice'].max(), df['latestPrice'].min(), df.iloc[-1,0], df.iloc[-1,1] - df.iloc[0,1]
    ch, chp = 0 if self.df is None else c - self.df.iloc[-1, 4], 0 if self.df is None else round(100*((c -self.df.iloc[-1, 4])/self.df.iloc[-1,4]),3)
    d, m = datetime.today().strftime('%m-%m-%y'),datetime.fromtimestamp(self.start_time + (self.record_count * self.interval)).strftime('%H:%M:%S')
    record = pd.DataFrame([{'date':d,'minute': m, 'open': o, 'high': h, 'low': l, 'close': c, 'volume':v, 'change': ch, 'changePercent': chp}])[['date','minute','open','high','low','close','volume','change','changePercent']]
    self.df = record if self.df is None else pd.concat([self.df,record])
    return None, time.time()

class QuoteStreamer(IEXClient):
    def __init__(self, symbol, **kwargs):
        #kwargs --> run_time (int) number of seconds to run
        #       --> interval (int) number of seconds between records, must be divisible by run_time
        IEXClient.__init__(self, symbol)
        self.run_time, self.interval, self.df = kwargs.get('run_time',1800), kwargs.get('interval',15), None
        self.records, self.record_count = self.run_time / self.interval, 0        
        self.yield_frames(60-int(datetime.fromtimestamp(time.time()).strftime('%H:%M:%S')[-2:]))

    def yield_quotes(self):
        for message in self.get_quote_stream():
            q = json.loads(message.data)
            if q:
                yield pd.DataFrame([q[0]])[['latestPrice','volume','latestTime','latestUpdate']]
            
    def yield_frames(self, pause):
        self.start_time = time.time() + pause
        time.sleep(pause)
        df, start_time = None, time.time()
        for quote in self.yield_quotes():
            df = quote if df is None else pd.concat([df, quote])
            if time.time() - start_time > self.interval:
                df, start_time = add_record(self, df)
                self.record_count += 1
            if self.record_count == self.records:
                return

#q = QuoteStreamer('AMD')
#q.df.to_csv('AMD_historicals_15s.csv',index=False)

