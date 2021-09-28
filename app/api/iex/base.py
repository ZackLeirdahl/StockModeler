import requests, json
import pandas as pd
from sseclient import SSEClient  
                     
class IEXClient:

    URLS = {
        'account': 'https://cloud.iexapis.com/v1/account/{}',
        'base': 'https://cloud.iexapis.com/v1/stock/{}/{}',
        'collection': 'https://cloud.iexapis.com/v1/stock/market/collection/{}',
        'market': 'https://cloud.iexapis.com/v1/stock/market/{}',
        'macro' : 'https://cloud.iexapis.com/v1/data-points/market/{}',
        'ref_data': 'https://cloud.iexapis.com/v1/ref-data/{}',
        'stream': 'https://cloud-sse.iexapis.com/stable/{}?token={}&symbols={}'
        }
    
    FIELDS = {
        'company': ['exchange','industry','sector','tags'],
        'advanced_stats': ['revenuePerShare','revenuePerEmployee','debtToEquity','profitMargin','enterpriseValue','enterpriseValueToRevenue','priceToSales','priceToBook','forwardPERatio','pegRatio','peRatio','peHigh','peLow'],
        'quote': ['change','changePercent','iexAskPrice','iexAskSize','iexBidPrice','iexBidSize','iexRealtimeSize','latestPrice','latestTime','latestUpdate','volume'],
        'balance_sheet': ['accountsPayable', 'capitalSurplus', 'commonStock', 'currentAssets', 'currentCash', 'currentLongTermDebt', 'goodwill', 'intangibleAssets', 'inventory', 'longTermDebt', 'longTermInvestments', 'minorityInterest', 'netTangibleAssets', 'otherAssets', 'otherCurrentAssets', 'otherCurrentLiabilities', 'otherLiabilities', 'propertyPlantEquipment', 'receivables', 'reportDate', 'retainedEarnings', 'shareholderEquity', 'shortTermInvestments', 'totalAssets', 'totalCurrentLiabilities', 'totalLiabilities', 'treasuryStock'],
        'income_statement': ['costOfRevenue', 'ebit', 'grossProfit', 'incomeTax', 'interestIncome', 'netIncome', 'netIncomeBasic', 'operatingExpense', 'operatingIncome', 'otherIncomeExpenseNet', 'pretaxIncome', 'reportDate', 'researchAndDevelopment', 'sellingGeneralAndAdmin', 'totalRevenue'],
        'cash_flow': ['capitalExpenditures', 'cashChange', 'cashFlow', 'cashFlowFinancing', 'changesInInventories', 'changesInReceivables', 'depreciation', 'dividendsPaid', 'exchangeRateEffect', 'investingActivityOther', 'investments', 'netBorrowings', 'otherFinancingCashFlows', 'reportDate', 'totalInvestingCashFlows'],
        'financials': ['currentDebt', 'operatingRevenue', 'reportDate', 'shortTermDebt', 'totalCash', 'totalDebt'],
        'news': ['datetime','hasPaywall','headline','related','source','summary','url'],
        'key_stats': ['marketcap', 'employees', 'float', 'ttmEPS', 'ttmDividendRate', 'companyName', 'sharesOutstanding', 'nextDividendDate', 'dividendYield', 'nextEarningsDate', 'exDividendDate', 'beta'],
        'analyst': ['updateDate','buy', 'hold', 'sell', 'ratingScaleMark', 'priceTargetAverage', 'priceTargetHigh', 'priceTargetLow', 'numberOfAnalysts', 'consensusEPS', 'numberOfEstimates', 'reportDate', 'fiscalPeriod', 'fiscalEndDate'],
        'valuation': ['peRatio','priceToBook','priceToSales','pegRatio','forwardPERatio','revenuePerEmployee','enterpriseValueToRevenue'],
        'ownership': ['entityProperName','adjHolding','adjMv','reportDate'],
        'minute': ['date','minute','open','high','low','close','volume'],
        'daily': ['date','open','high','low','close','change','changePercent','volume'],
        'list': ['change','changePercent','high','highTime','latestPrice','low','lowTime','previousClose','previousVolume','symbol','volume'],
        'earnings_today': ['announceTime','consensusEPS','currency','fiscalEndDate','fiscalPeriod','numberOfEstimates','reportDate','symbol']}
    
    ENDPOINTS = {
        'base': ['key_stats','advanced_stats','balance_sheet','cash_flow','earnings','financials','income_statement','company','dividends','estimates','fund_ownership','insider_roster','insider_summary','insider_transactions','institutional_ownership'],
        'commodities': ['oil','natural_gas','heating_oil','jet_fuel','diesel','gas','propane'],
        'economic_data': ['daily_treasury_rates','cpi','cc_interest_rates','fed_fund_rate','real_gdp','imf','initial_claims','industrial_production_interest','mortgage_rates','total_housing_starts','total_payrolls','total_vehicle_sales','retail_money_funds','unemployment_rate','recession_probability']
    }
    
    def __init__(self, symbol=None):
        self.symbol = symbol.upper() if symbol else None
        self.session, self.token = requests.session(), 'pk_a06a25225ada4526b58688e6a1bf95c4'
        
    def request(self, url, params={}):
        response = self.session.get(url=url, params={**{'token':self.token}, **{k: str(v).lower() if isinstance(v,bool) else str(v) for k, v in params.items()}})
        return response.json()

    def fetch(self, endpoint, url=None, params={}):
        return self.request(self.URLS['base'].format(self.symbol,endpoint) if not url else self.URLS[url].format(endpoint), params)

    def stream(self, endpoint):
        return SSEClient(self.URLS['stream'].format(endpoint,self.token,self.symbol))
    
    ### account api calls ###
    def get_usage(self):
        self.token = 'sk_c7bf589a15d04f3585c8313ea6c47d5b'
        return self.fetch('usage/messages','account')

    def get_metadata(self):
        self.token = 'sk_c7bf589a15d04f3585c8313ea6c47d5b'
        return self.fetch('metadata', 'account')
    
    def get_messages_by_endpoint(self):
        return self.get_usage()['keyUsage']
    
    def get_messages_by_day(self):
        return self.get_usage()['dailyUsage']
    
    def get_messages_remaining(self, pct=True):
        data = self.get_metadata()
        return data['messageLimit'] - data['messagesUsed'] if not pct else 100 - round(100*(data['messagesUsed'] / data['messageLimit']),2)

    ### base api calls ###
    def get_base(self):
        return {ep: getattr(self,'get_%s' % ep)() for ep in self.ENDPOINTS['base']}

    def get_key_stats(self, **kwargs):
        return {k: round(v*100,2) if 'Percent' in k else v for k, v in self.fetch('stats', params=kwargs).items() if k in self.FIELDS['key_stats']} 
		
    def get_advanced_stats(self, **kwargs):
        return {k: round(v*100,2) if k == 'profitMargin' else (round(v,2) if type(v) == float else v) for k, v in self.fetch('advanced-stats', params=kwargs).items() if k in self.FIELDS['advanced_stats']}

    def get_balance_sheet(self, **kwargs):
        return pd.DataFrame(list(map(lambda x: {k:v for k, v in x.items() if k in self.FIELDS['balance_sheet']}, self.fetch('balance-sheet', params=kwargs)['balancesheet'])))
	
    def get_cash_flow(self, **kwargs):
        return pd.DataFrame(list(map(lambda x: {k:v for k, v in x.items() if k in self.FIELDS['cash_flow']}, self.fetch('cash-flow', params=kwargs)['cashflow'])))

    def get_earnings(self, **kwargs):
        return pd.DataFrame(list(map(lambda x: {k if k != 'fiscalEndDate' else 'reportDate': v for k, v in x.items()}, self.fetch('earnings', params=kwargs)['earnings'])))

    def get_financials(self, **kwargs):
        return pd.DataFrame(list(map(lambda x: {k:v for k, v in x.items() if k in self.FIELDS['financials']}, self.fetch('financials', params=kwargs)['financials'])))
    
    def get_income_statement(self, **kwargs):
        return pd.DataFrame(list(map(lambda x: {k:v for k, v in x.items() if k in self.FIELDS['income_statement']}, self.fetch('income', params=kwargs)['income'])))

    def get_company(self, **kwargs):
        return {k:v for k, v in self.fetch('company', params=kwargs).items() if k in self.FIELDS['company']}

    def get_dividends(self, **kwargs):
        return pd.DataFrame(self.fetch('dividends', params=kwargs))

    def get_estimates(self):
        return self.fetch('estimates')['estimates'][0]

    def get_fund_ownership(self):
        df = pd.DataFrame(self.fetch('fund-ownership'))
        df['reportDate'] = df['report_date']
        return df[self.FIELDS['ownership']]

    def get_insider_roster(self):
        return pd.DataFrame(self.fetch('insider-roster'))

    def get_insider_summary(self):
        return pd.DataFrame(self.fetch('insider-summary'))

    def get_insider_transactions(self):
        return pd.DataFrame(self.fetch('insider-transactions'))

    def get_institutional_ownership(self):
        return pd.DataFrame(self.fetch('institutional-ownership'))[self.FIELDS['ownership']]

    def get_historical_prices(self, **kwargs):
        return pd.DataFrame(self.fetch('chart', params=kwargs))

    def get_recommendation_trends(self):
        r = self.fetch('recommendation-trends')[0]
        r['buy'], r['sell'], r['hold'] =  r['ratingBuy'] + r['ratingOverweight'], r['ratingSell'] + r['ratingUnderweight'], r['ratingHold']
        return r
        
    def get_news(self, **kwargs):
        return pd.DataFrame(self.fetch('news', params=kwargs))[self.FIELDS['news']]

    def get_previous_day_prices(self):
        return pd.Series({k:v for k, v in self.fetch('previous').items() if k != 'symbol'})[self.FIELDS['daily']]

    def get_book(self):
        return self.fetch('book')
        
    def get_price(self):
        return self.fetch('price')

    def get_price_target(self):
        return self.fetch('price-target')
    
    def get_peers(self):
        return {'peers': self.fetch('peers')}

    def get_quote(self, **kwargs):
        return self.fetch('quote', params=kwargs)

    def get_volume_by_venue(self):
        return pd.DataFrame(self.fetch('volume-by-venue'))

    ## collection api calls ##
    def get_most_active(self):
        return pd.DataFrame(self.fetch('list','collection',{'collectionName':'mostactive'}))[self.FIELDS['list']]

    def get_gainers(self):
        return pd.DataFrame(self.fetch('list','collection',{'collectionName':'gainers'}))[self.FIELDS['list']]
    
    def get_losers(self):
        return pd.DataFrame(self.fetch('list','collection',{'collectionName':'losers'}))[self.FIELDS['list']]

    ## market api calls ##
    def get_market_volume(self):
        return pd.DataFrame(self.fetch('volume','market'))
    
    def get_earnings_today(self):
        data = self.fetch('today-earnings','market')
        return pd.DataFrame(data['bto']+data['amc'])[self.FIELDS['earnings_today']]

    def get_sector_performance(self):
        return pd.DataFrame(self.fetch('sector-performance','market'))

    ## ref_data api calls ##
    def get_ref_data(self, collection='tags'):
        """ collection: tags or sectors """
        return self.fetch(collection,'ref_data')
    
    ### macro api calls ###
    ### commodoties
    def get_commodities(self):
        return pd.DataFrame([(commodity, getattr(self, 'get_{}_prices'.format(commodity))()) for commodity in self.ENDPOINTS['commodities']])

    def get_oil_prices(self, brent=False):
        return self.fetch('DCOILWTICO' if not brent else 'DCOILBRENTEU','macro')
    
    def get_natural_gas_prices(self):
        return self.fetch('DHHNGSP','macro')
    
    def get_heating_oil_prices(self):
        return self.fetch('DHOILNYH','macro')

    def get_jet_fuel_prices(self):
        return self.fetch('DJFUELUSGULF','macro')
    
    def get_diesel_prices(self):
        return self.fetch('GASDESW','macro')
    
    def get_gas_prices(self):
        return self.fetch('GASREGCOVW','macro')
    
    def get_propane_prices(self):
        return self.fetch('DPROPANEMBTX','macro')

    ### economic data ###
    def get_economic_data(self):
        return pd.DataFrame([(data_point, getattr(self, 'get_{}'.format(data_point))()) for data_point in self.ENDPOINTS['economic_data']])
    
    def get_daily_treasury_rates(self, rate=30):
        return self.fetch('DGS' + str(rate),'macro')

    def get_cpi(self):
        return self.fetch('CPIAUCSL','macro')

    def get_cc_interest_rates(self):
        return self.fetch('TERMCBCCALLNS','macro')
    
    def get_fed_fund_rate(self):
        return self.fetch('FEDFUNDS','macro')
    
    def get_real_gdp(self):
        return self.fetch('A191RL1Q225SBEA','macro')
    
    def get_imf(self):
        return self.fetch('WIMFSL','macro')
    
    def get_initial_claims(self):
        return self.fetch('IC4WSA','macro')
    
    def get_industrial_production_interest(self):
        return self.fetch('INDPRO','macro')
    
    def get_mortgage_rates(self, length=30):
        return self.fetch('MORTGAGE30US' if length == 30 else ('MORTGAGE15US' if length == 15 else 'MORTGAGE5US'),'macro')
    
    def get_total_housing_starts(self):
        return self.fetch('HOUST','macro')
    
    def get_total_payrolls(self):
        return self.fetch('PAYEMS','macro')
    
    def get_total_vehicle_sales(self):
        return self.fetch('TOTALSA','macro')
    
    def get_retail_money_funds(self):
        return self.fetch('WRMFSL','macro')
    
    def get_unemployment_rate(self):
        return self.fetch('UNRATE','macro')
    
    def get_recession_probability(self):
        return self.fetch('RECPROUSM156N','macro')

    ### stream api calls ###
    def get_quote_stream(self):
        return self.stream('stocksUSNoUTP')
    
    def get_news_stream(self):
        return self.stream('news-stream')
