from email.mime.application import MIMEApplication
import pandas as pd
from django.conf import settings
import matplotlib.pyplot as plt
from django.apps import AppConfig 
from .utils import functions
from .utils.micro_macro_functions import micro_functions
from .models import Stock
import logging
import datetime
import seaborn as sns

class stock_analytics_send_foreign_daily(AppConfig):
    def __init__(self, app_name: str, app_module: None) -> None:
        super().__init__(app_name, app_module)

    def run(self):
        try:
            self.send_1_day()
        except Exception:
            logging.warn("Process Failed")

    def send_1_day(self):
        try:
            three_months_ago = datetime.date.today() - datetime.timedelta(days=40)
            stocks = Stock.objects.filter(date__gte=three_months_ago)
            
            stock_data = [stock.__dict__ for stock in stocks]
            df = pd.DataFrame(stock_data)

            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values(by=['stock_name', 'date'])
            df['1_day_return'] = df.groupby('stock_name')['close_price'].transform(lambda x: (x / x.shift(1) - 1) * 100)
            df.dropna(subset=['1_day_return'], inplace=True)
            top_gainers_daily = df.sort_values(by='1_day_return', ascending=False).head(30)
            top_tickers = top_gainers_daily['stock_name'].unique()
            print(top_tickers)

            n_rows = (len(top_tickers) + 3) // 3  # Add 2 to ensure all tickers are plotted
            n_cols = 3

            sns.set_style("whitegrid")
            plt.rcParams.update({'font.size': 19})

            fig, axes = plt.subplots(n_rows, n_cols, figsize=(21, 5 * n_rows))

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
            functions.send_png_tg(plt, caption='Foreign Stock Analysis: Daily Maximum returns')
            logging.info('Plot sent successfully to Telegram.')

            plt.close(fig)

        except Exception as e:
            logging.error(f'Foreign Failed to send plot: {str(e)}')















