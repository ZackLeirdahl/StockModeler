import pandas as pd
import numpy as np

class Signal:
    def __init__(self, df, **kwargs):
        self.name, self.n, self.decimal, self.ntiles, self.vals_only = None, None, 2, kwargs.get('ntiles'), kwargs.get('vals_only', True)
    
    def finish(func):
        def wrapper(self):
            df = func(self).astype('float64')
            if not self.vals_only:
                df = self.additional_columns(df).astype('object')
            df.loc[:self.n-1,:] = np.nan
            return df[[col for col in df if np.isin(df[col].dropna().unique(), [0.0, 1.0]).all()]] if not self.vals_only else df
        return wrapper

    @finish
    def run(self):
        return pd.DataFrame(self.calculate().apply(lambda x: round(x,self.decimal)))
    
    def additional_columns(self, df):
        return df


        