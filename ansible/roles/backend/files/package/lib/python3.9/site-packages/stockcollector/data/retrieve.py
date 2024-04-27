from django.shortcuts import render
import datetime
from .models import Stock
from .utils.functions import get_day_of_the_month, get_stock_prices, get_yesterday
from .utils.micro_macro_functions import micro_functions
import pandas as pd 
from django.conf import settings
from django.apps import AppConfig 
from .apps import AppConfig
from .models import Stock

class stocks(AppConfig):
    def __init__(self, app_name: str, app_module: None) -> None:
        super().__init__(app_name, app_module)

    def run(self):
        time = datetime.datetime.now()
        print('hello world:[{}]'.format(time))
        startDate = '2023-01-01'
        endDate = get_day_of_the_month()
        company = []
        stock_data = pd.DataFrame()

        for key, value in settings.COMPANIES['default'].items():
            company.append(value)

        for companies in company:
        #     # Fetch data using get_stock_prices
              data = get_stock_prices(startDate, endDate, companies)
              stock_data = pd.concat([stock_data, data])
        print(data)
        print(stock_data)    
        # Process and calculate values
        stock_data.reset_index(drop=True, inplace=True)  # Update in-place
        stock_data['count'] = stock_data.index
        micro_functions.calc_vol(stock_data)

        # Delete the table firs
        Stock.objects.all().delete()
        # Save data to database using Django ORM
        Stock.objects.bulk_create([
            Stock(
                date=row['Date'],
                open_price=row['Open'],  # Renamed
                high_price=row['High'],  # Renamed
                low_price=row['Low'],  # Renamed
                close_price=row['Close'],  # Renamed
                volume=row['Volume'],
                stock_name=row['ticker'],  # Renamed
                daily_return=row['returns'],  # Renamed
                volatility=row['volatility'],
                daily_change=row['change'],  # Renamed
                high_low_spread=row['hi_low_spread'],
                expected_change=row['exp_change'],
            ) for _, row in stock_data.iterrows()
        ])
    # except Exception as e:  # Catch specific exceptions (e.g., ConnectionError)
    #     print(f"Error retrieving data: {e}")
