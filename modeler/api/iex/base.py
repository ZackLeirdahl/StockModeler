import requests, json
import pandas as pd
from sseclient import SSEClient  
                     
class IEXClient:

    urls = {
        'base': 'https://cloud.iexapis.com/v1/stock/market/batch/', 
        'stream': 'https://cloud-sse.iexapis.com/stable/{}?token={}&symbols={}'}
    
    fields = {
        'company': ['exchange','industry','sector','tags'],
        'advanced_stats': ['revenuePerShare','revenuePerEmployee','debtToEquity','profitMargin','enterpriseValue','enterpriseValueToRevenue','priceToSales','priceToBook','forwardPERatio','pegRatio','peRatio','peHigh','peLow'],
        'quote': ['change','changePercent','iexAskPrice','iexAskSize','iexBidPrice','iexBidSize','iexRealtimeSize','latestPrice','latestTime','latestUpdate','volume'],
        'balance_sheet': ['accountsPayable', 'capitalSurplus', 'commonStock', 'currentAssets', 'currentCash', 'currentLongTermDebt', 'goodwill', 'intangibleAssets', 'inventory', 'longTermDebt', 'longTermInvestments', 'minorityInterest', 'netTangibleAssets', 'otherAssets', 'otherCurrentAssets', 'otherCurrentLiabilities', 'otherLiabilities', 'propertyPlantEquipment', 'receivables', 'reportDate', 'retainedEarnings', 'shareholderEquity', 'shortTermInvestments', 'totalAssets', 'totalCurrentLiabilities', 'totalLiabilities', 'treasuryStock'],
        'income_statement': ['costOfRevenue', 'ebit', 'grossProfit', 'incomeTax', 'interestIncome', 'netIncome', 'netIncomeBasic', 'operatingExpense', 'operatingIncome', 'otherIncomeExpenseNet', 'pretaxIncome', 'reportDate', 'researchAndDevelopment', 'sellingGeneralAndAdmin', 'totalRevenue'],
        'cash_flow': ['capitalExpenditures', 'cashChange', 'cashFlow', 'cashFlowFinancing', 'changesInInventories', 'changesInReceivables', 'depreciation', 'dividendsPaid', 'exchangeRateEffect', 'investingActivityOther', 'investments', 'netBorrowings', 'otherFinancingCashFlows', 'reportDate', 'totalInvestingCashFlows'],
        'financials': ['currentDebt', 'operatingRevenue', 'reportDate', 'shortTermDebt', 'totalCash', 'totalDebt'],
        'news': ['datetime','hasPaywall','headline','related','source','summary','url'],
        'key_stats': ['marketcap', 'employees', 'float', 'ttmEPS', 'ttmDividendRate', 'companyName', 'sharesOutstanding', 'nextDividendDate', 'dividendYield', 'nextEarningsDate', 'exDividendDate', 'beta'],
        'analyst': ['updateDate','ratingBuy', 'ratingOverweight', 'ratingHold', 'ratingUnderweight', 'ratingSell', 'ratingNone', 'ratingScaleMark', 'priceTargetAverage', 'priceTargetHigh', 'priceTargetLow', 'numberOfAnalysts', 'consensusEPS', 'numberOfEstimates', 'reportDate', 'fiscalPeriod', 'fiscalEndDate'],
        'valuation': ['peRatio','priceToBook','priceToSales','pegRatio','forwardPERatio','revenuePerEmployee','enterpriseValueToRevenue'],
        'minute': ['date','minute','open','high','low','close','volume'],
        'daily': ['date','open','high','low','close','change','changePercent','volume']}
    
    def __init__(self, symbol=None, **kwargs):
        self.symbol = symbol.upper()
        self.session = requests.session()
        self.token = kwargs.get('token','pk_a06a25225ada4526b58688e6a1bf95c4')

    def params(self, endpoint, optional_params = {}):
        return {**{'symbols': self.symbol,'types': endpoint, 'token': self.token}, **{k: str(v).lower() if v is True or v is False else str(v) for k, v in optional_params.items()}}

    def fetch(self, endpoint, params={}, stream=False):
        response = self.session.get(url=self.urls['base'], params=self.params(endpoint,params)) if not stream else SSEClient(self.urls['stream'].format(endpoint,self.token,self.symbol))
        return response.json()[self.symbol][endpoint] if not stream else response
    
    def get_key_stats(self, **kwargs):
        return {k: round(v*100,2) if 'Percent' in k else v for k, v in self.fetch('stats', params=kwargs).items() if k in self.fields['key_stats']} 
		
    def get_advanced_stats(self, **kwargs):
        return {k: round(v*100,2) if k == 'profitMargin' else (round(v,2) if type(v) == float else v) for k, v in self.fetch('advanced-stats', params=kwargs).items() if k in self.fields['advanced_stats']}

    def get_balance_sheet(self, **kwargs):
        return pd.DataFrame(list(map(lambda x: {k:v for k, v in x.items() if k in self.fields['balance_sheet']}, self.fetch('balance-sheet', params=kwargs)['balancesheet'])))
	
    def get_cash_flow(self, **kwargs):
        return pd.DataFrame(list(map(lambda x: {k:v for k, v in x.items() if k in self.fields['cash_flow']}, self.fetch('cash-flow', params=kwargs)['cashflow'])))

    def get_earnings(self, **kwargs):
        return pd.DataFrame(list(map(lambda x: {k if k != 'fiscalEndDate' else 'reportDate': v for k, v in x.items()}, self.fetch('earnings', params=kwargs)['earnings'])))

    def get_financials(self, **kwargs):
        return pd.DataFrame(list(map(lambda x: {k:v for k, v in x.items() if k in self.fields['financials']}, self.fetch('financials', params=kwargs)['financials'])))
    
    def get_income_statement(self, **kwargs):
        return pd.DataFrame(list(map(lambda x: {k:v for k, v in x.items() if k in self.fields['income_statement']}, self.fetch('income', params=kwargs)['income'])))

    def get_company(self, **kwargs):
        return {k:v for k, v in self.fetch('company', params=kwargs).items() if k in self.fields['company']}

    def get_dividends(self, **kwargs):
        return pd.DataFrame(self.fetch('dividends', params=kwargs))

    def get_estimates(self):
        return self.fetch('estimates')['estimates'][0]

    def get_fund_ownership(self):
        return pd.DataFrame(self.fetch('fund-ownership'))

    def get_insider_roster(self):
        return pd.DataFrame(self.fetch('insider-roster'))

    def get_insider_summary(self):
        return pd.DataFrame(self.fetch('insider-summary'))

    def get_insider_transactions(self):
        return pd.DataFrame(self.fetch('insider-transactions'))

    def get_institutional_ownership(self):
        return pd.DataFrame(self.fetch('institutional-ownership'))

    def get_historical_prices(self, **kwargs):
        return pd.DataFrame(self.fetch('chart', params=kwargs))

    def get_recommendation_trends(self):
        return self.fetch('recommendation-trends')
        
    def get_news(self, **kwargs):
        return pd.DataFrame(self.fetch('news', params=kwargs))[self.fields['news']]

    def get_previous_day_prices(self):
        return {k:v for k, v in self.fetch('previous').items() if k != 'symbol'}

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

    def get_quote_stream(self):
        return self.fetch('stocksUSNoUTP',stream=True)
    
    def get_news_stream(self):
        return self.fetch('news-stream',stream=True)

