from email.mime.application import MIMEApplication
import pandas as pd
from django.conf import settings
import matplotlib.pyplot as plt
from django.apps import AppConfig 
from .utils import functions
from .utils.micro_macro_functions import micro_functions
from .models import StockBST
import logging

class stock_analytics_bist(AppConfig):
    def __init__(self, app_name: str, app_module: None) -> None:
        super().__init__(app_name, app_module)

    def run(self):
        try:
            self.send_analytics()
        except Exception:
            logging.warn("Process Failed")
        
    def send_analytics(self):
        try:
            stocks = StockBST.objects.all()

            stock_data = [stock.__dict__ for stock in stocks]

            df = pd.DataFrame(stock_data)
            data_to_be_sent = micro_functions.daily_screen(df)

            #sending part:
            functions.send_csv(data_to_be_sent, caption='Analytics Report')
            functions.send_message('BIST Data succesfully sent')
            logging.info('BIST CSV sent successfully to Telegram')

        except Exception as e:
            logging.error(f'Failed to send CSV: {str(e)}')
 
        try:
            ticker_performance = df.groupby('stock_name').apply(
                lambda x: (x['close_price'].iloc[-1] - x['close_price'].iloc[0]) / x['close_price'].iloc[0] * 100
            ).sort_values(ascending=False)
            
            top_tickers = ticker_performance.head(20).index
            filtered_df = df[df['stock_name'].isin(top_tickers)]
            
            n_rows = len(top_tickers)  
            n_cols = 3  

            n_rows = (len(top_tickers) + n_cols - 1) // n_cols  

            fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5 * n_rows)) 

            for i, ticker in enumerate(top_tickers):
                row = i // n_cols
                col = i % n_cols
                ax = axes[row, col] if n_rows > 1 else axes[col]

                subset = filtered_df[filtered_df['stock_name'] == ticker]
                ax.plot(subset['date'], subset['close_price'])
                ax.set_title(f'BIST Stock Prices for {ticker}', fontsize=14, fontweight='bold')
                ax.set_xlabel('Date', fontsize=12, fontweight='bold')
                ax.set_ylabel('Close Price', fontsize=12, fontweight='bold')

                ax.text(subset['date'].iloc[0], subset['close_price'].iloc[0], f'{subset["close_price"].iloc[0]:.2f}', fontsize=10,
                        ha='center', va='bottom', fontweight='bold')
                ax.text(subset['date'].iloc[-1], subset['close_price'].iloc[-1], f'{subset["close_price"].iloc[-1]:.2f}', fontsize=10,
                        ha='center', va='bottom', fontweight='bold')

            for i in range(len(top_tickers), n_rows * n_cols):
                fig.delaxes(axes.flatten()[i])

            plt.tight_layout()

            functions.send_png(plt, caption='BIST Top 20 Ticker Performance')
            logging.info('BIST Plot sent successfully to Telegram')

        except Exception as e:
            logging.error(f'BIST Failed to send plot: {str(e)}')















