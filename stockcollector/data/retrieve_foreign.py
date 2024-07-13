import datetime
import pandas as pd
from django.conf import settings
from .models import Stock
from .utils.micro_macro_functions import micro_functions
from .utils.functions import get_stock_prices
import logging
from django.apps import AppConfig

class Stocks(AppConfig):
    def __init__(self, app_name: str, app_module: None) -> None:
        super().__init__(app_name, app_module)

    def run(self):
        try:
            self.retrieve_data()
        except Exception as e:
            logging.warning(f"Process failed: {str(e)}")

    def retrieve_data(self):
        current_date = datetime.datetime.now()
        print(f"Stock Data collection has started: [{current_date}]")

        start_date = "2022-01-01"
        end_date = current_date.strftime("%Y-%m-%d")  # Use today's date for end date

        companies = list(settings.COMPANIES["default"].values())

        batch_size = 10  # Adjust the batch size according to your memory constraints
        for i in range(0, len(companies), batch_size):
            batch_companies = companies[i:i + batch_size]
            self.process_batch(batch_companies, start_date, end_date)

        print("Stock data updated successfully.")

    def process_batch(self, companies, start_date, end_date):
        stock_data = pd.DataFrame()

        for company in companies:
            try:
                data = get_stock_prices(start_date, end_date, company)
                if data is not None:
                    stock_data = pd.concat([stock_data, data])
                else:
                    logging.warning(f"No data returned for company: {company}")
            except Exception as e:
                logging.warning(f"Failed to retrieve data for company {company}: {str(e)}")

        # Process and calculate values
        if stock_data.empty:
            logging.warning("No stock data to process for this batch.")
            return

        stock_data.reset_index(drop=True, inplace=True)
        micro_functions.calc_vol(stock_data)

        # Check for existing data in the database
        existing_entries = Stock.objects.values_list('stock_name', 'date')
        existing_entries = set(existing_entries)

        new_entries = []
        for _, row in stock_data.iterrows():
            if (row["ticker"], row["Date"]) not in existing_entries:
                new_entry = Stock(
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

        # Bulk create new entries in smaller batches to prevent memory issues
        batch_size = 1000  # Adjust this size based on your memory constraints
        for i in range(0, len(new_entries), batch_size):
            Stock.objects.bulk_create(new_entries[i:i + batch_size])
            logging.info(f"Inserted batch {i//batch_size + 1}")

        print("Stock data updated successfully.")
