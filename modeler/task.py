from util import build_schedule
from api.api import API
from firebase import Firebase

class Task:
    attrs = ['collection','key','df','data','interval','new','finish_task']
    
    def __init__(self, *args, **kwargs):
        self.name, self.type, self.symbol, self.args, self.outputs = args[0], args[1], args[2].upper(), args[3:], []
        self.prepare(*args, **kwargs)
    
    def __str__(self):
        return 'Name: {}\nType: {}\nSymbol: {}'.format(self.name, self.type, self.symbol)

    def prepare(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self,k,v)
        for attr in list(set(self.attrs) - set(kwargs.keys())):
            setattr(self,attr,None)
        if 'finish_kwargs' not in dir(self):
            self.finish_kwargs = {}
        self.kwargs = kwargs
        
    def do(self, *args, **kwargs):
        return

class ClientTask(Task):
    def __init__(self,  *args, **kwargs):
        Task.__init__(self, *args, **kwargs)

    def do(self, *args, **kwargs):
        if self.name == 'new_intraday_options':
            self.outputs.append(Task('options', 'APITask', self.symbol, **{'interval':'dynamic', 'dummy':True}))
        if self.name == 'new_intraday_historicals':
            self.outputs.append(Task('historicals', 'APITask', self.symbol, **{'interval':self.uri.split('.')[0].split('_')[-1]}))
        if self.name in ['intraday_historicals', 'archive_dynamic']:
            self.outputs.append(Task('get', 'FireTask', self.symbol, self.uris, finish_task=self.name))
        if self.name in ['daily','intraday_options']:
            self.outputs += [Task('get', 'FireTask', self.symbol, uri, finish_task=uri.split('/')[0], finish_kwargs={'interval':uri.split('/')[-1].split('.')[0].split('_')[-1]}) for uri in self.uris]
        if self.name == 'new':
            self.outputs += ([Task(name, 'APITask', self.symbol, **{'interval':'daily'}) for name in ['historicals','options']] if self.daily else []) + ([Task(artifact, 'APITask', self.symbol) for artifact in artifacts] if self.artifacts else []) + ([Task('company_data', 'APITask', self.symbol, **{'collection':'company'}), Task('post', 'FireTask', self.symbol, 'schedule', self.symbol, build_schedule(self)),Task('delete', 'FireTask', self.symbol,'new', self.symbol)])
        if self.name == 'stocks':
            self.outputs.append(Task('post', 'FireTask', self.symbol, 'new', self.symbol, self.kwargs))
        if self.name == 'schedule':
            self.outputs.append(Task('post', 'FireTask', self.symbol,'schedule', self.symbol, build_schedule(self)))
        if self.name == 'average_volume':
            self.outputs.append(Task('get','FireTask',self.symbol, self.uris[0], finish_task=self.name, finish_kwargs={'interval':self.uris[0].split('/')[-1].split('.')[0].split('_')[-1]}))
        if self.name == 'archive_timeseries':
            self.outputs.append(Task('get', 'FireTask',self.symbol, self.uris[0], finish_task=self.name))
        if self.name == 'scorecard':
            self.outputs.append(Task('get','FireTask', self.symbol, self.uris[0], finish_task=self.name, finish_kwargs={'interval': self.interval}))
        return self.outputs


class FireTask(Task):
    def __init__(self, *args, **kwargs):
        Task.__init__(self, *args, **kwargs)
    
    def do(self, *args, **kwargs):
        data = getattr(Firebase(),self.name)(*self.args, **self.kwargs)
        self.outputs = [Task(self.finish_task, 'APITask', self.symbol, data, **self.finish_kwargs)] if data is not None and type(data) != bool and all(data) else []
        return self.outputs

class APITask(Task):
    def __init__(self, *args, **kwargs):
        Task.__init__(self, *args, **kwargs)
    
    def do(self, *args, **kwargs):
        data = API(self.symbol, self.name, self.args, **self.kwargs).outputs
        if type(data) == list:
            self.outputs += [Task('post', 'FireTask', self.symbol, output['uri'], output['df']) for output in data]
        elif 'collection' in data.keys():
            self.outputs.append(Task('post', 'FireTask', self.symbol, data['collection'], data['key'], data['data']))
        else:
            self.outputs.append(Task('post', 'FireTask', self.symbol, data['uri'], data['df']))
        return self.outputs
