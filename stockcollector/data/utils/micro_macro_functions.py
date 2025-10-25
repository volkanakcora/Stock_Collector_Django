import numpy as np
import pandas as pd
from .functions import get_yesterday
import logging

class micro_functions:
    def __init__(self, symbol, key, folder=None):
        self.symbol = symbol
        self.key = key
        self.folder = folder

    @staticmethod
    def calc_vol(df):
        """
        Volatilite ve diğer istatistikleri hesapla
        
        Args:
            df: OHLCV verisi içeren DataFrame
        """
        # Boş DataFrame kontrolü
        if df.empty:
            return
        
        # DEBUG: Fonksiyon versiyonu
        logging.info("✓ calc_vol() V2.0 - FIXED VERSION")
            
        # Kolon isimlerini esnek kullan (Close veya close_price)
        close_col = 'Close' if 'Close' in df.columns else 'close_price'
        high_col = 'High' if 'High' in df.columns else 'high_price'
        low_col = 'Low' if 'Low' in df.columns else 'low_price'
        open_col = 'Open' if 'Open' in df.columns else 'open_price'
        
        # Getiri hesaplama - Series olarak al (FIX için kritik!)
        close_series = df[close_col]
        df['returns'] = np.log(close_series).diff().round(4)
        
        # Volatilite (21 günlük rolling std)
        df['volatility'] = df['returns'].rolling(21).std().round(4)
        
        # Günlük değişim
        df['change'] = close_series.diff()
        
        # Yüksek-düşük spread
        high_series = df[high_col]
        low_series = df[low_col]
        open_series = df[open_col]
        df['hi_low_spread'] = ((high_series - low_series) / open_series).round(2)
        
        # Beklenen değişim
        df['exp_change'] = (df['volatility'] * close_series.shift(1)).round(2)
        
        # Magnitude (büyüklük)
        df['magnitude'] = (df['change'] / df['exp_change']).round(2)
        df['abs_magnitude'] = np.abs(df['magnitude'])
        
        # NaN satırları temizle
        df.dropna(inplace=True)
    
    @staticmethod
    def calc_vol_for_ml(df):
        """
        ML için volatilite hesaplama (lowercase kolonlar için)
        
        Args:
            df: OHLCV verisi içeren DataFrame
        """
        # Boş DataFrame kontrolü
        if df.empty:
            return
            
        # Getiri hesaplama - Series olarak al
        close_series = df['close_price']
        df['returns'] = np.log(close_series).diff().round(4)
        
        # Volatilite (21 günlük rolling std)
        df['volatility'] = df['returns'].rolling(21).std().round(4)
        
        # Günlük değişim
        df['change'] = close_series.diff()
        
        # Yüksek-düşük spread (büyük harfli kolonlar kullanılıyor)
        high_series = df['High']
        low_series = df['Low']
        open_series = df['Open']
        df['hi_low_spread'] = ((high_series - low_series) / open_series).round(2)
        
        # Beklenen değişim
        df['exp_change'] = (df['volatility'] * close_series.shift(1)).round(2)
        
        # Magnitude (büyüklük)
        df['magnitude'] = (df['change'] / df['exp_change']).round(2)
        df['abs_magnitude'] = np.abs(df['magnitude'])
        
        # NaN satırları temizle
        df.dropna(inplace=True)

    @staticmethod
    def daily_screen(df):
        df = df[df['date'] == str(get_yesterday())]
        df = df.sort_values(by=['daily_change'], ascending=False)
        return df.head(50)

    @staticmethod
    def monitor_stocks(df):
        df['1_day_return'] = (df['close_price'] / df['close_price'].shift(1) - 1) * 100
        df['3_days_return'] = (df['close_price'] / df['close_price'].shift(3) - 1) * 100
        df['5_days_return'] = (df['close_price'] / df['close_price'].shift(5) - 1) * 100
        
        df['volume_change_1_week'] = (df['volume'].rolling(window=5).mean() / df['volume'].rolling(window=5).mean().shift(1) - 1) * 100
        
        df['3_months_return'] = (df['close_price'] / df['close_price'].shift(63) - 1) * 100  # Assuming 21 trading days per month
        
        top_gainers_1_day = df.sort_values(by='1_day_return', ascending=False).head(10)
        top_gainers_3_days = df.sort_values(by='3_days_return', ascending=False).head(10)
        top_gainers_5_days = df.sort_values(by='5_days_return', ascending=False).head(10)
        high_volume_stocks = df.sort_values(by='volume', ascending=False).head(10)
        
        biggest_decliners_3_months = df.sort_values(by='3_months_return').head(10)
        increased_volume_recently = biggest_decliners_3_months.sort_values(by='volume_change_1_week', ascending=False).head(10)
        
        return (top_gainers_1_day, top_gainers_3_days, top_gainers_5_days, high_volume_stocks,
                biggest_decliners_3_months, increased_volume_recently)
    
    @staticmethod
    def plot_stock_prices(data, x_column='date', y_column='close_price', title_prefix='Stock Prices', n_cols=3):
        """
        Plot stock prices from a DataFrame.

        Parameters:
        - data (pd.DataFrame): DataFrame containing the data with columns 'x_column' and 'y_column'.
        - x_column (str): Column name in data DataFrame representing the x-axis values (default is 'date').
        - y_column (str): Column name in data DataFrame representing the y-axis values (default is 'close_price').
        - title_prefix (str): Prefix for the plot title (default is 'Stock Prices').
        - n_cols (int): Number of columns for subplots (default is 3).

        Returns:
        - None

        """
        try:
            n_rows = (len(data) + n_cols - 1) // n_cols

            fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5 * n_rows))

            for i, (index, row) in enumerate(data.iterrows()):
                row_idx = i // n_cols
                col_idx = i % n_cols
                ax = axes[row_idx, col_idx] if n_rows > 1 else axes[col_idx]

                ax.plot(row[x_column], row[y_column])
                ax.set_title(f'{title_prefix} for {row["stock_name"]}', fontsize=14, fontweight='bold')
                ax.set_xlabel('Date', fontsize=12, fontweight='bold')
                ax.set_ylabel('Close Price', fontsize=12, fontweight='bold')

                ax.text(row[x_column].iloc[0], row[y_column].iloc[0], f'{row[y_column].iloc[0]:.2f}', fontsize=10,
                        ha='center', va='bottom', fontweight='bold')
                ax.text(row[x_column].iloc[-1], row[y_column].iloc[-1], f'{row[y_column].iloc[-1]:.2f}', fontsize=10,
                        ha='center', va='bottom', fontweight='bold')

            for i in range(len(data), n_rows * n_cols):
                fig.delaxes(axes.flatten()[i])

            plt.tight_layout()
            plt.show()

        except Exception as e:
            logging.error(f'Failed to plot stock prices: {e}')










