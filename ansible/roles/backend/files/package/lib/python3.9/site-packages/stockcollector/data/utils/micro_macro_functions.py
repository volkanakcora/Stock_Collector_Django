import numpy as np
import pandas as pd
from .functions import get_yesterday

class micro_functions:
    def __init__(self, symbol, key, folder=None):
        self.symbol = symbol
        self.key = key
        self.folder = folder

    def calc_vol(df):
        df['returns'] = np.log(df.Close).diff().round(4)
        df['volatility'] = df.returns.rolling(21).std().round(4)
        df['change'] = df['Close'].diff()
        df['hi_low_spread'] = ((df['High'] - df['Low']) / df['Open']).round(2)
        df['exp_change'] = (df.volatility * df.Close.shift(1)).round(2)
        df['magnitude'] = (df.change / df.exp_change).round(2)
        df['abs_magnitude'] = np.abs(df.magnitude)
        df.dropna(inplace= True)

    def daily_screen(df):
        df = df[df['date'] == str(get_yesterday())]
        df = df.sort_values(by=['daily_change'], ascending=False)
        return df.head(50)









