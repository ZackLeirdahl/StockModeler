import pandas as pd
import time, json
try:
    from base import IEXClient
except:
    from .base import IEXClient

class QuoteStreamer(IEXClient):
    def __init__(self, symbol):
        IEXClient.__init__(self, symbol, **kwargs)
        self.run_time = kwargs.get('run_time',30)
        self.yield_time = kwargs.get('yield_time',5)
        self.yielding = True
        self.df = None
        self.process_frames()

    def yield_quotes(self):
        for message in self.get_quote_stream():
            yield pd.DataFrame([{k: v for k, v in json.loads(message.data)[0].items() if k in ['latestPrice','volume','latestTime','latestUpdate']}])
            
    def yield_frames(self):
        df = None
        start_time = time.time()
        for quote in self.yield_quotes():
            df = quote if df is None else pd.concat([df, quote])
            if time.time() - start_time > self.yield_time:
                yield df
                df = None
            if time.time() - start_time > self.run_time:
                break

    def process_frames(self):
        for df in self.yield_frames():
            self.df = df if self.df is None else pd.concat([self.df,df])

#q = QuoteStreamer('AMD')
"""
- start at beginning of day
- yield time will yield every n seconds
    - when yielded, send to process:
        - get volume over the period
        - get OHLC over the period
            - add that row to the next longer interval frame
        EX: every 1 minute
"""