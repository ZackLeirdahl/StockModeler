import pandas as pd
from api import API, Artifacts, Historicals, ChainMeasurements, StockProfile, Scorecard
from api.robinhood import Client, Chain, Portfolio, Order
from api.technical_analysis import Technicals
from firebase import Firebase
from task import Task, FireTask, ClientTask, APITask

def robinhood_client():
    c = Client()

def historicals(symbol, **kwargs):
    h = Historicals(symbol, **kwargs)
    return h.df

def measurements(symbol, **kwargs):
    m = ChainMeasurements(symbol, **kwargs)
    return m.df

def technicals(uri, **kwargs):
    t = Technicals(Firebase().get(uri), **kwargs)
    return t.df

def scorecard(uri, **kwargs):
    s = Scorecard(Firebase().get(uri), **kwargs)
    return s.scorecard()

def artifacts():
    a = Artifacts('AMD','analyst')
    print(a.df)

def profile():
    p = StockProfile('AMD','company_data')
    print(p.data)

def api(symbol, task, inp, **kwargs):
    a = API(symbol, task, inp, **kwargs)
    return a.outputs

def do_task(t):
    t.__class__ = eval(t.type)
    ft = t.do()[0]
    ft.__class__ = eval(ft.type)
    at = ft.do()[0]
    at.__class__ = eval(at.type)
    ft = at.do()[0]
    ft.__class__ = eval(ft.type)
    ft.do()

def intraday_option_archive(symbol):
    do_task(Task('archive_dynamic','ClientTask', symbol, **{'uris': ['options/{}_options_dynamic.csv'.format(symbol),'options/{}_options_dynamic_archive.csv'.format(symbol)]}))

def timeseries_archive(symbol):
    do_task(Task('archive_timeseries','ClientTask', symbol, **{'uris': ['options/{}_options_dynamic_archive.csv'.format(symbol)]}))

def scorecard_task(symbol, interval):
    do_task(Task('scorecard','ClientTask', symbol, **{'uris': ['historicals/{}_historicals_{}.csv'.format(symbol,interval)], 'interval':interval}))

def begin():
    robinhood_client()
    post(api('AMD','options',(), interval='dynamic'))

def finish():
    intraday_option_archive('AMD')
    timeseries_archive('AMD')

def get(uri):
    return Firebase().get(uri)

def post(data):
    if 'df' in data.keys():
        Firebase().post(data['uri'], data['df'])
    else:
        Firebase().post(data['collection'], data['key'], data['data'])


#begin()
post(api('AMD','options',get('options/AMD_options_dynamic.csv'), interval='dynamic'))
#finish()


""" historicals """
#historicals('AMD',new=True)
#historicals('AMD',interval='dynamic')
#historicals('AMD',new=True, interval='minute')
#historicals('AMD',new=True, interval=30)
#historicals('AMD',interval=10).to_csv('AMD_historicals_10.csv', index=False)

""" measurements """
#measurements('AMD',interval='dynamic')
#measurements('AMD',interval='daily')

""" technicals """
#technicals('historicals/AMD_historicals_daily.csv')
#print(technicals('historicals/AMD_historicals_daily.csv', overlays=False))
#technicals('historicals/AMD_historicals_daily.csv', indicators=False)
#technicals('historicals/AMD_historicals_daily.csv', change_only=True)
#technicals('historicals/AMD_historicals_daily.csv', vals_only=False)
#technicals('historicals/AMD_historicals_daily.csv', vals_only=False, include_historicals=False)

""" scorecard """
#scorecard('historicals/AMD_historicals_10.csv').to_csv('AMD_scorecard_10.csv',index=False)
#scorecard('historicals/AMD_historicals_daily.csv').to_csv('AMD_scorecard_daily.csv',index=False)

""" api """
#api('AMD','historicals',(), interval='dynamic')
#post(api('AMD','historicals',(), interval='daily'))
#post(api('AMD','options',(), interval='dynamic'))

#post(api('AMD','options',(), interval='daily'))
##api('AMD','company_data',(), collection='company')
#post(api('AMD','historicals',(), interval='10'))
#post(api('AMD','options',get('options/AMD_options_dynamic.csv'), interval='dynamic'))
#post(api('AMD','historicals',(),interval='10'))
#robinhood_client()
#api('AMD','options',(), interval='dynamic')
#get('historicals/AMD_historicals_daily.csv').to_csv('AMD_historicals_daily.csv',index=False)
#get('historicals/AMD_historicals_10.csv').to_csv('AMD_historicals_10.csv',index=False)
#get('historicals/AMD_historicals_30.csv').to_csv('AMD_historicals_30.csv',index=False)
#get('options/AMD_options_timeseries.csv').to_csv('AMD_options_timeseries.csv', index=False)
#get('options/AMD_options_dynamic_archive.csv').to_csv('AMD_options_dynamic_archive.csv', index=False)
#c = Chain('AMD')
#print(c.get_active_options(limit=10))
#print(c.get_active_options(limit=10, option_type='put'))
#scorecard_task('AMD','10')
""" TO DO
- further scorecard analyzer for decision making
    - add scorecard to firestore?
- build a full cycle option order
    - place order
    - verify it has executed
    - monitor it
- tweak average implied volatility calculation for dynamic options
"""    