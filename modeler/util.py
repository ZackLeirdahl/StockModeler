def build_schedule(self):
    return {
        'archive': {'uris': ['options/'+'_'.join([self.symbol,'options','daily','archive']) + '.csv', 'options/'+'_'.join([self.symbol,'options','dynamic','archive']) + '.csv']},
        'daily': {'execute': self.daily, 'uris':['historicals/'+'_'.join([self.symbol,'historicals','daily']) + '.csv', 'options/'+'_'.join([self.symbol,'options','daily']) + '.csv' ]}, 
        'intraday':{
            'historicals':{'execute':self.intraday_historicals, 'interval':self.intraday_historicals_interval, 'uris':['historicals/'+'_'.join([self.symbol,'historicals','10']) + '.csv','historicals/'+'_'.join([self.symbol,'historicals','30']) + '.csv']},
            'options':{'execute':self.intraday_options, 'interval':self.intraday_options_interval, 'uris':['options/'+'_'.join([self.symbol,'options','dynamic']) + '.csv']}}}
