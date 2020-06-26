def oauth():
    return 'https://api.robinhood.com/oauth2/token/'

def challenge(id):
    return 'https://api.robinhood.com/challenge/{}/respond/'.format(id)

def stock(symbol):
    return 'https://api.robinhood.com/instruments/?symbol={}'.format(symbol)

def option_chain():
    return 'https://api.robinhood.com/options/chains/'

def account(account_id):
    return 'https://api.robinhood.com/accounts/{}/'.format(account_id)

def accounts():
    return 'https://api.robinhood.com/accounts/'

def portfolio(account_id):
    return 'https://api.robinhood.com/accounts/{}/portfolio/'.format(account_id)

def quote():
    return 'https://api.robinhood.com/marketdata/quotes'

def options():
    return 'https://api.robinhood.com/options/instruments/'

def option_marketdata():
    return 'https://api.robinhood.com/marketdata/options/'

def stock_order(id):
    return 'https://api.robinhood.com/orders/{}/'.format(id)

def stock_orders():
    return 'https://api.robinhood.com/orders/'

def stock_positions():
    return 'https://api.robinhood.com/positions/'

def option_order(id):
    return 'https://api.robinhood.com/options/orders/{}/'.format(id)

def option_orders():
    return 'https://api.robinhood.com/options/orders/'

def option_positions():
    return 'https://api.robinhood.com/options/positions/'
