import os, time
import pandas as pd
from datetime import datetime
from .measurements import ChainMeasurements
from .historicals import Historicals
from .artifacts import Artifacts

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
        return self.blob_task()

    @finish_blob
    def blob_task(self):
        obj = ChainMeasurements(self.symbol, input=self.input, interval=self.kwargs.get('interval'), dummy=self.kwargs.get('dummy')) if self.task == 'options' else (Historicals(self.symbol, **{**self.kwargs,**{'input':self.input}}) if self.task == 'historicals' else Artifacts(self.symbol, self.task, input=self.input))
        return obj.data
    