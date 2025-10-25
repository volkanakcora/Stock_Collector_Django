import datetime
import pandas as pd
from django.conf import settings
from .models import Stock
from .utils.micro_macro_functions import micro_functions
from .utils.functions import get_stock_prices
import logging
import time
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
        """Yabancı hisse senetlerinden veri çekme işlemi - Basit ve direkt"""
        current_date = datetime.datetime.now()
        print(f"Foreign Stock Data collection has started: [{current_date}]")

        start_date = "2024-01-01"
        end_date = current_date.strftime("%Y-%m-%d")  

        companies = list(settings.COMPANIES["default"].values())
        
        print(f"📊 Toplam {len(companies)} foreign stock çekilecek")
        print("⚠️  Yahoo Finance rate limiting nedeniyle yavaş çalışacak...")

        stock_data = pd.DataFrame()

        # WORKAROUND: Her hisse için rate limiting ile veri çek
        for idx, company in enumerate(companies, 1):
            print(f"[{idx}/{len(companies)}] {company} çekiliyor...")
            
            data = get_stock_prices(start_date, end_date, company)
            
            if data is not None and not data.empty:
                stock_data = pd.concat([stock_data, data], ignore_index=True)
                print(f"  ✓ {company}: {len(data)} satır eklendi")
            else:
                print(f"  ✗ {company}: Veri alınamadı")
            
            # WORKAROUND: Her 5 hisseden sonra 10 saniye bekle (rate limit)
            if idx % 5 == 0 and idx < len(companies):
                print("  ⏸️  Rate limit için 10s bekleniyor...")
                time.sleep(10)

