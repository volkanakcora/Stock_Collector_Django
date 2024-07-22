import pandas as pd
from django.conf import settings
import matplotlib.pyplot as plt
from django.apps import AppConfig 
from .utils import functions
from .utils.micro_macro_functions import micro_functions
from .models import StockBST
import logging
import datetime
import seaborn as sns 
class stock_analytics_bist(AppConfig):
    def __init__(self, app_name: str, app_module: None) -> None:
        super().__init__(app_name, app_module)

    def run(self):
        try:
            self.send_analytics()
            self.send_last_3_months()
        except Exception as e:
            logging.warn(f"Process Failed:  {str(e)}")
        
    def send_analytics(self):
        try:
            stocks = StockBST.objects.all()

            stock_data = [stock.__dict__ for stock in stocks]

            df = pd.DataFrame(stock_data)

        except Exception as e:
            logging.error(f'Failed to retrieve data from database: {str(e)}')
 
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
    
    def send_last_3_months(self):
        try:
            three_months_ago = datetime.date.today() - datetime.timedelta(days=3*40)
            stocks =  StockBST.objects.filter(date__gte=three_months_ago)
             
            stock_data = [stock.__dict__ for stock in stocks]

            df = pd.DataFrame(stock_data)

            df = df[df['date'].between(df['date'].max() - pd.DateOffset(months=3), df['date'].max())]

            df['date'] = pd.to_datetime(df['date'])

            df = df.sort_values(by=['stock_name', 'date'])

            df['3_months_return'] = df.groupby('stock_name')['close_price'].transform(lambda x: (x / x.shift(63) - 1) * 100)

            end_date = df['date'].max()
            start_date = end_date - pd.DateOffset(months=3)
            last_3_months = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

            threshold = 7 

            losing_stocks = last_3_months[last_3_months['3_months_return'] < threshold]['stock_name'].unique()

            filtered_stocks = df[df['stock_name'].isin(losing_stocks)]

            filtered_stocks['volume_change_5_days'] = filtered_stocks.groupby('stock_name')['volume'].transform(lambda x: (x.rolling(window=5).mean() / x.rolling(window=5).mean().shift(5) - 1) * 100)

            volume_increase_threshold = 100  
            significant_volume_increase = filtered_stocks[filtered_stocks['volume_change_5_days'] > volume_increase_threshold]

            latest_data = significant_volume_increase.sort_values('date').drop_duplicates('stock_name', keep='last')

            latest_data = latest_data[latest_data['3_months_return'] < threshold]
            top_tickers = latest_data.stock_name.unique()

            n_rows = (len(top_tickers) + 2) // 2  
            n_cols = 2

            sns.set_style("whitegrid")
            plt.rcParams.update({'font.size': 19})

            fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 5 * n_rows))

            for i, ticker in enumerate(top_tickers):
                row = i // n_cols
                col = i % n_cols
                ax = axes[row, col] if n_rows > 1 else axes[col]

                subset = df[df['stock_name'] == ticker]
                
                ax.plot(subset['date'], subset['close_price'], label='Close Price', color='tab:blue', linewidth=2)

                ax2 = ax.twinx()
                ax2.bar(subset['date'], subset['volume'], color='tab:orange', alpha=1, label='Volume')

                ax.set_title(f'{ticker}', fontsize=19, fontweight='bold')
                ax.set_xlabel('Date', fontsize=18)
                ax.set_ylabel('Close Price', fontsize=18, color='tab:blue')
                ax2.set_ylabel('Volume', fontsize=18, color='tab:orange')

                ax.grid(True, which='both', linestyle='--', linewidth=0.1)

                ax.set_xticks(subset['date'][::10]) 
                ax.set_xticklabels([date.strftime('%b-%y') for date in subset['date'][::10]], rotation=45, ha='right')

                ax.text(subset['date'].iloc[0], subset['close_price'].iloc[0], f'{subset["close_price"].iloc[0]:.2f}', fontsize=10,
                        ha='center', va='bottom', fontweight='bold', color='tab:blue')
                ax.text(subset['date'].iloc[-1], subset['close_price'].iloc[-1], f'{subset["close_price"].iloc[-1]:.2f}', fontsize=10,
                        ha='center', va='bottom', fontweight='bold', color='tab:blue')

                ax.legend(loc='upper left')
                ax2.legend(loc='upper right')

            for i in range(len(top_tickers), n_rows * n_cols):
                fig.delaxes(axes.flatten()[i])

            plt.tight_layout(rect=[0, 0, 1, 0.97])
            plt.show()

            functions.send_png_tg(plt, caption='BIST Stock Analysis: 3-Month Decline with Recent Surge in Trading Volume')
            logging.info('Plot sent successfully to Telegram.')

            plt.close(fig)

        except Exception as e:
            logging.error(f'BIST Failed to send plot: {str(e)}')















