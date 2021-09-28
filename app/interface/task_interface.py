import pandas as pd
from ..firebase import Firebase
from ..api.api import API
"""
TO DO
find a way to get interval/kwargs to each task i.e. interval for options
"""

class TaskInterface:
    def __init__(self, symbols, tasks, interval):
        self.symbols = symbols if type(symbols) == list else [symbols]
        self.tasks = tasks if type(tasks) == list else [tasks]
        self.interval = interval
        self.symbol_tasks = {s:self.tasks for s in self.symbols}
        self.do_tasks()

    def do_tasks(self):
        for sym, tasks in self.symbol_tasks.items():
            for t in tasks:
                if t in ['options','historicals']:
                    self.do_interval_task(sym, t)
                else:
                    self.do_task(sym, t)

    def do_interval_task(self, symbol, task):
        inp = Firebase().get('{}/{}_{}_{}.csv'.format(task,symbol,task,self.interval))
        data = API(symbol, task, inp if isinstance(inp, pd.DataFrame) else (), interval=self.interval).outputs
        Firebase().post(data['uri'], data['df'])

    def do_task(self, symbol, task):
        inp = Firebase().get('{}/{}_{}.csv'.format(task, symbol, task))
        data = API(symbol, task, inp if isinstance(inp,pd.DataFrame) else ()).outputs
        Firebase().post(data['uri'], data['df'])

def get_option_symbols():
    return Firebase().extract_keys('options','dynamic')

