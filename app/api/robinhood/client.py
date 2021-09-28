import json, requests
try:
    from util import user_input
    from wrappers import authorize, post_login, pre_login
    from endpoints import oauth, challenge, stock_orders, option_orders
except:
    from .util import user_input
    from .wrappers import authorize, post_login, pre_login
    from .endpoints import oauth, challenge, stock_orders, option_orders
    
class Client(object):
    
    HEADERS = {'Accept': '*/*','Accept-Encoding': 'gzip, deflate','Accept-Language': ('en;q=1, fr;q=0.9, de;q=0.8, ja;q=0.7, ' +'nl;q=0.6, it;q=0.5'), 'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) ' + 'AppleWebKit/537.36 (KHTML, like Gecko) ' + 'Chrome/68.0.3440.106 Safari/537.36')}
    def __init__(self, *args, **kwargs):
        self.access_token, self.authenticated = None, False
        self.login()
    
    @authorize
    def get(self, url=None, params=None, retry=True):
        res = requests.get(url,headers=self.HEADERS,params=params,timeout=15,verify=r'C:\Users\zleirdahl\Documents\GitHub\StockModeler\certs.pem')
        return res.json() if res.status_code != 400 else None

    @authorize
    def post(self, url=None, payload=None, extra_headers={}, retry=True):
        if url in [option_orders(),stock_orders()]:
            self.HEADERS['Content-Type'] = 'application/json; charset=utf-8'
        res = requests.post(url, headers={**self.HEADERS, **extra_headers}, data=json.dumps(payload), timeout=15, verify=r'C:\Users\zleirdahl\Documents\GitHub\StockModeler\certs.pem')
        return res.json() if res.headers['Content-Length'] != '0' else None
    
    @pre_login
    @post_login
    def login(self):
        if self.authenticated:
            with open(r'C:\Users\zleirdahl\Documents\GitHub\StockModeler\robinhood_auth.json', 'r') as f:
                return json.loads(f.read())
        return self.post(oauth(), payload=self.payload, extra_headers={'X-ROBINHOOD-CHALLENGE-RESPONSE-ID': self.post(challenge(self.post(oauth(), payload=self.payload)['challenge']['id']),{'response': user_input()})['id']})
