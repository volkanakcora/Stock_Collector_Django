from email.mime.application import MIMEApplication
import pandas as pd
from django.conf import settings
import matplotlib.pyplot as plt
from django.apps import AppConfig 
from .utils import functions
from .utils.micro_macro_functions import micro_functions
from .models import Stock
import logging

class stock_analytics(AppConfig):
    def __init__(self, app_name: str, app_module: None) -> None:
        super().__init__(app_name, app_module)

    def run(self):
        try:
            self.send_analytics()
        except Exception:
            logging.warn("Process Failed")
        
    def send_analytics(self):     

        # Query all data from the Stock model using Django ORM
        stocks = Stock.objects.all()

        # Convert the queryset to a list of dictionaries
        stock_data = [stock.__dict__ for stock in stocks]

        # Create a pandas dataframe from the list of dictionaries
        df = pd.DataFrame(stock_data)
        # send the data
        data_to_be_Sent = micro_functions.daily_screen(df)
        functions.send_email(self, data_to_be_Sent, settings.EMAILS['default']['1'])
        logging.info('Email has been sent successfully')
        # Prepare plot
        # Calculate the price change percentage for each ticker
        ticker_performance = df.groupby('stock_name').apply(
            lambda x: (x['close_price'].iloc[-1] - x['close_price'].iloc[0]) / x['close_price'].iloc[0] * 100)
        ticker_performance = ticker_performance.sort_values(ascending=False)

        # Select the top 10 best-performing tickers
        top_tickers = ticker_performance.head(20).index

        # Filter the DataFrame to keep only the data for the top tickers
        filtered_df = df[df['stock_name'].isin(top_tickers)]
        # Calculate the date 4 months ago from the current date
        today = functions.get_day_of_the_month()
        four_months_ago = today - pd.DateOffset(months=4)

        # Filter the DataFrame for the last 4 months
        filtered_df = filtered_df[filtered_df['date'] >= four_months_ago]
        # List of unique tickers
        tickers = filtered_df['stock_name'].unique()
        # Define the number of rows and columns for the grid
        n_rows = len(tickers)  # You can adjust this based on the number of tickers
        n_cols = 3  # You can adjust this based on the number of tickers

        # Create a figure and a grid of subplots
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 8 * len(tickers)))

        # Iterate through tickers and create subplots
        for i, ticker in enumerate(tickers):
            row = i // n_cols
            col = i % n_cols
            ax = axes[row, col]

            subset = filtered_df[filtered_df['stock_name'] == ticker]
            ax.plot(subset['date'], subset['close_price'])
            ax.set_title(f'Stock Prices for {ticker}')
            ax.set_xlabel('Date')
            ax.set_ylabel('Close Price')

            # Add data point labels (for example, label the first and last data points)
            ax.text(subset['date'].iloc[0], subset['close_price'].iloc[0], f'{subset["close_price"].iloc[0]:.2f}', fontsize=10,
                    ha='center', va='bottom')
            ax.text(subset['date'].iloc[-1], subset['close_price'].iloc[-1], f'{subset["close_price"].iloc[-1]:.2f}', fontsize=10,
                    ha='center', va='bottom')

        # Remove any empty subplots
        for i in range(len(tickers), n_rows * n_cols):
            fig.delaxes(axes.flatten()[i])
        
        plt.savefig('stock_prices.png')


        # Adjust layout for better spacing
        plt.tight_layout()
        # send the plots
        functions.send_image(self, plt, settings.EMAILS['default']['1'])
        logging.info('Graph has been sent successfully')















