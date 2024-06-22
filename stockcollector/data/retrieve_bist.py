import datetime
import pandas as pd
from django.conf import settings
from .models import StockBST
from .utils.micro_macro_functions import micro_functions
from .utils.functions import get_stock_prices, get_day_of_the_month, get_yesterday
import logging
from django.apps import AppConfig 

class StocksBST(AppConfig):
    def __init__(self, app_name: str, app_module: None) -> None:
        super().__init__(app_name, app_module)

    def run(self):
        try:
            self.retrieve_data()
        except Exception as e:
            logging.warn(f"Process failed: {str(e)}")

    def retrieve_data(self):
        current_date = datetime.datetime.now()
        print(f"Stock Data collection has started: [{current_date}]")

        start_date = "2023-02-01"
        end_date = current_date.strftime("%Y-%m-%d")  # Use today's date for end date

        companies = list(settings.COMPANIES_BIST["default"].values())

        stock_data = pd.DataFrame()

        for company in companies:
            data = get_stock_prices(start_date, end_date, company)
            stock_data = pd.concat([stock_data, data])

        # Process and calculate values
        stock_data.reset_index(drop=True, inplace=True)
        micro_functions.calc_vol(stock_data)

         # Check for existing data in database
        existing_entries = StockBST.objects.values_list('stock_name', 'date')
        existing_entries = set(existing_entries)

        new_entries = []
        for _, row in stock_data.iterrows():
            if (row["ticker"], row["Date"]) not in existing_entries:
                new_entry = StockBST(
                    date=row["Date"],
                    open_price=row["Open"],
                    high_price=row["High"],
                    low_price=row["Low"],
                    close_price=row["Close"],
                    volume=row["Volume"],
                    stock_name=row["ticker"],
                    daily_return=row["returns"],
                    volatility=row["volatility"],
                    daily_change=row["change"],
                    high_low_spread=row["hi_low_spread"],
                    expected_change=row["exp_change"],
                )
                new_entries.append(new_entry)

        # Bulk create new entries
        logging.info(new_entries)
        StockBST.objects.bulk_create(new_entries)

        print("Stock data updated successfully.")
