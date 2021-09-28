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

def scorecard(uri, descriptor, **kwargs):
    s = Scorecard(Firebase().get(uri), descriptor, **kwargs)
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

def score_task(symbol, interval):
    do_task(Task('score', 'ClientTask',symbol, **{'uris': ['scorecard/{}_scorecard_{}.csv'.format(symbol,interval)], 'interval':interval}))

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




#post(api('AMD','options',(), interval='dynamic'))
#post(api('NOK','options',(), interval='dynamic'))
#post(api('RBLX','options',(), interval='dynamic'))
#post(api('TLRY','options',(), interval='dynamic'))
#post(api('CLOV','options',(), interval='dynamic'))
#robinhood_client()
#begin()
#post(api('NOK','options',get('options/NOK_options_dynamic.csv'), interval='dynamic'))
post(api('AMD','options',get('options/AMD_options_dynamic.csv'), interval='dynamic'))
#post(api('RBLX','options',get('options/RBLX_options_dynamic.csv'), interval='dynamic'))
#post(api('CLOV','options',get('options/CLOV_options_dynamic.csv'), interval='dynamic'))
#finish()
#print(Firebase().extract_keys())
""" historicals """
#historicals('AMD',new=True)
#historicals('AMD',interval='dynamic')
#historicals('AMD',new=True, interval=30)
#historicals('AMD',interval=10).to_csv('AMD_historicals_10.csv', index=Fal#e)

""" measurements """
#measurements('AMD',interval='dynamic')
#measurements('AMD',interval='daily')

""" technicals """
#technicals('historicals/AMD_historicals_daily.csv')
#print(technicals('historicals/AMD_historicals_daily.csv', overlays=False))
#technicals('historicals/AMD_historicals_daily.csv').to_csv('AMD_technicals_daily.csv',index=False)
#technicals('historicals/AMD_historicals_daily.csv', change_only=True)
#technicals('historicals/AMD_historicals_daily.csv', vals_only=False).to_csv('AMD_technicals_daily.csv',index=False)
#technicals('historicals/AMD_historicals_daily.csv', vals_only=False, include_historicals=False)

""" scorecard """
#scorecard('historicals/AMD_historicals_10.csv').to_csv('AMD_scorecard_10.csv',index=False)
#scorecard('historicals/AMD_historicals_daily.csv', 'daily').to_csv('AMD_scorecard_daily.csv',index=False)
#0
""" api """
#post(api('AMD','analyst',()))
#post(api('AMD','historicals',(), interval='minute'))
#post(api('AMD','historicals',(), interval='10'))
#post(api('AMD','options',(), interval='dynamic'))
#get('scorecard/AMD_scorecard_daily.csv').to_csv('AMD_scorecard_daily.csv',index=False)
#post(api('AMD','historicals',(), interval='daily'))
##api('AMD','company_data',(), collection='company')
#post(api('AMD','historicals',(), interval='minute'))
#post(api('AMD','options',get('options/AMD_options_dynamic.csv'), interval='dynamic'))
#post(api('AMD','historicals',(),interval='daily'))
#robinhood_client()
#api('AMD','options',(), interval='dynamic')
#get('historicals/AMD_historicals_daily.csv').to_csv('AMD_historicals_daily.csv',index=False)
#get('historicals/AMD_historicals_minute.csv').to_csv('AMD_historicals_minute.csv',index=False)
#get('scorecard/AMD_scorecard_daily.csv').to_csv('AMD_scorecard_daily.csv',index=False)
#get('scorecard/AMD_scorecard_minute.csv').to_csv('AMD_scorecard_minute.csv',index=False)
#get('options/AMD_options_timeseries.csv').to_csv('AMD_options_timeseries.csv', index=False)
#get('options/AMD_options_dynamic_archive.csv').to_csv('AMD_options_dynamic_archive.csv', index=False)
#print(get('scores/AMD_scores_daily.csv'))
#scorecard_task('AMD','minute')
#score_task('AMD','daily')
#c = Chain('amd')
#x = c.get_active_options(limit=10).to_dict('records') + c.get_active_options(option_type='put',limit=10).to_dict('records')
#print(x)
#print(c.get_max_pain())

#print(c.get_active_options(limit=10))
#print(c.get_active_options(limit=10, option_type='put'))
#print(c.get_option_spread().to_dict('records'))

#print(c.get_active_options(limit=10).to_html(classes="td-custom"))
#artifacts()
""" TO DO
- build a full cycle option order
    - place order
    - verify it has executed
    - monitor it
- tweak average implied volatility calculation for dynamic options
"""   
