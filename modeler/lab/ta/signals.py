import pandas as pd
import numpy as np

class Signal:
    def __init__(self, df, **kwargs):
        self.name, self.n, self.decimal, self.ntiles = None, None, 2, kwargs.get('ntiles')
    
    def finish(func):
        def wrapper(self):
            df = func(self).astype('float64')
            df = self.additional_columns(df).astype('object')
            df.loc[:self.n-1,:] = np.nan
            return df[[col for col in df if np.isin(df[col].dropna().unique(), [0.0, 1.0]).all()]]
        return wrapper

    @finish
    def run(self):
        return pd.DataFrame(self.calculate().apply(lambda x: round(x,self.decimal)))
    
    def additional_columns(self, df):
        return df


        