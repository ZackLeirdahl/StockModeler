import json, requests
try:
    from util import user_input
    from wrappers import authorize, post_login, pre_login
    from endpoints import oauth, challenge
except:
    from .util import user_input
    from .wrappers import authorize, post_login, pre_login
    from .endpoints import oauth, challenge
    
class Client(object):
    
    headers = {"Accept": "*/*","Accept-Encoding": "gzip, deflate","Accept-Language": ("en;q=1, fr;q=0.9, de;q=0.8, ja;q=0.7, " +"nl;q=0.6, it;q=0.5"), "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) " + "AppleWebKit/537.36 (KHTML, like Gecko) " + "Chrome/68.0.3440.106 Safari/537.36")}
    
    def __init__(self, *args, **kwargs):
        self.username = kwargs.get('username','zackleirdahl@gmail.com')
        self.password = kwargs.get('password','Aksahc123!')
        self.access_token = None
        self.authenticated = False
        self.login()
    
    @authorize
    def get(self, url=None, params=None, retry=True):
        res = requests.get(url,headers=self.headers,params=params,timeout=15,verify='certs.pem')
        return res.json()

    @authorize
    def post(self, url=None, payload=None, extra_headers={}, retry=True):
        res = requests.post(url, headers={**self.headers, **extra_headers}, data=json.dumps(payload), timeout=15, verify='certs.pem')
        return res.json() if res.headers['Content-Length'] != '0' else None
    
    @pre_login
    @post_login
    def login(self):
        if self.authenticated:
            with open('robinhood_auth.json', 'r') as f:
                return json.loads(f.read())
        return self.post(oauth(), payload=self.payload, extra_headers={'X-ROBINHOOD-CHALLENGE-RESPONSE-ID': self.post(challenge(self.post(oauth(), payload=self.payload)['challenge']['id']),{'response': user_input()})['id']})

