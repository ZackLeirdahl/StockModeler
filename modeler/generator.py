import os
import pandas as pd
from datetime import datetime, timedelta
from task import ClientTask as Task
from firebase import Firebase

def runtimes(interval=None):
    if interval:
        runtimes = [':'.join(str(timedelta(hours=8,minutes=30) + timedelta(minutes=interval*(i+1))).split(':')[:-1]) for i in range(int(390/interval))]
        return [runtime if len(runtime) == 5 else '0' + runtime for runtime in runtimes]
    runtime = ':'.join(str(timedelta(hours=datetime.now().hour, minutes=datetime.now().minute) + timedelta(minutes=1)).split(':')[:-1])
    return runtime if len(runtime) == 5 else '0' + runtime

def check_uris(uris):
    return [uri for uri in uris if type(Firebase().get(uri)) == bool]

def rename_file(fname, directory):
    os.rename(os.path.join(directory,fname),os.path.join(directory,'_' + fname.split('.')[0] + '_' + str(len([f for f in os.listdir(directory) if f[0] == '_'])) +'.csv'))

class TaskGenerator:
    def __init__(self):
        self.tasks = []
    
    def get_tasks(self, task_type, test=False):
        return getattr(self,  task_type + '_tasks')(test=test)

    def intraday_tasks(self, test=False):
        for sym, data in Firebase().get('schedule').items():
            if sym == 'AMD':
                for task, task_data in data.items():
                    if task == 'intraday':
                        for k, v in task_data.items():
                            if v['execute']:
                                new_uris = check_uris(v['uris'])
                                for uri in new_uris:
                                    self.tasks.append({'runtimes':[runtimes()],'task':Task('new_'+task+'_'+k,'ClientTask',  sym, **{'uri':uri, 'interval':v['interval']})})
                                if not test:
                                    self.tasks.append({'runtimes':runtimes(interval=v['interval']),'task':Task(task+'_'+k,'ClientTask',  sym, **{'interval':v['interval'], 'uris':[uri for uri in v['uris'] if uri not in new_uris]})})  
                                else:
                                    self.tasks.append({'runtimes':[runtimes()],'task':Task(task+'_'+k,'ClientTask',  sym, **{'interval':v['interval'], 'uris':[uri for uri in v['uris'] if uri not in new_uris]})})
        return self.tasks
    
    def daily_tasks(self, test=False):
        for sym, data in Firebase().get('schedule').items():
            for task, task_data in data.items():
                if task == 'daily' and task_data['execute']:
                    if not test:
                        self.tasks.append({'runtimes':['15:05'],'task':Task(task, 'ClientTask', sym, **task_data)})
                    else:
                        self.tasks.append({'runtimes':[runtimes()],'task':Task(task, 'ClientTask', sym, **task_data)})
        return self.tasks

    def staging_tasks(self, test=False):
        for f in [f for f in os.listdir('staging' if not test else 'test_staging') if f[0] != '_']:
            for k, v in {f.split('.')[0]: [{rec['symbol']: {k:v for k, v in rec.items() if k != 'symbol'} for rec in pd.read_csv(os.path.join('staging' if not test else 'test_staging',f)).to_dict('records')}]}.items():
                for rec in v:
                    for sym, data in rec.items():
                        self.tasks.append({'runtimes':[runtimes()], 'task': Task(k, 'ClientTask', sym, **data)})
            if not test:
                rename_file(f, 'staging')      
        return self.tasks

    def new_tasks(self, test=False):
        self.tasks += [{'runtimes':['15:05' if not test else runtimes()], 'task' : Task('new', 'ClientTask', sym, **data)} for sym, data in Firebase().get('new').items() if sym != 'Dummy2']
        return self.tasks
    
    def daily_archive_tasks(self, test=False):
        for sym, data in Firebase().get('schedule').items():
            self.tasks.append({'runtimes':[runtimes()], 'task': Task('archive_daily','ClientTask', sym, **{'uris': [data['daily']['uris'][1], data['archive']['uris'][0]]})})
        return self.tasks
    
    def dynamic_archive_tasks(self, test=False):
        for sym, data in Firebase().get('schedule').items():
            if sym == 'BAC':
                self.tasks.append({'runtimes':[runtimes()], 'task': Task('archive_dynamic','ClientTask', sym, **{'uris': [data['intraday']['options']['uris'][0], data['archive']['uris'][1]]})})
        return self.tasks
