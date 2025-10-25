import datetime
import http.client
import json
import pandas as pd
import logging
from django.apps import AppConfig
from .models import Fund

class Tefas(AppConfig):
    name = "tefas"

    def __init__(self, app_name: str, app_module: None) -> None:
        super().__init__(app_name, app_module)
        self.api_host = "tefas-api.p.rapidapi.com"
        self.api_key = "c3c297e087mshf0c09b3c9068e2fp1ae78fjsnf0b02d992e8a"
        self.api_headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': self.api_host
        }

    def run(self):
        """Main entry point"""
        try:
            self.retrieve_data()
        except Exception as e:
            logging.warning(f"TEFAS data process failed: {str(e)}")

    def retrieve_data(self):
        current_date = datetime.datetime.now()
        print(f"TEFAS Data collection started at [{current_date}]")

        # 🔁 Dinamik tarih aralıkları
        today = datetime.datetime.today()
        periods = {
            "1M": today - datetime.timedelta(days=30),
            "3M": today - datetime.timedelta(days=90),
            "6M": today - datetime.timedelta(days=180),
            "1Y": today - datetime.timedelta(days=365)
        }

        all_data = []
        conn = http.client.HTTPSConnection(self.api_host)

        for label, start_date in periods.items():
            start = start_date.strftime("%d.%m.%Y")
            end = today.strftime("%d.%m.%Y")
            print(f"➡️ {label} getirileri alınıyor: {start} - {end}")

            endpoint = f"/api/v1/funds/returns?fundType=1&startDate={start}&endDate={end}"
            conn.request("GET", endpoint, headers=self.api_headers)
            res = conn.getresponse()
            data = json.loads(res.read().decode("utf-8"))

            records = data.get("data", [])
            if not isinstance(records, list):
                records = [records] if records else []

            df = pd.DataFrame(records)
            if not df.empty:
                df["period"] = label
                all_data.append(df)

        if not all_data:
            logging.warning("⚠️ TEFAS API'den veri alınamadı.")
            return

        result = pd.concat(all_data, ignore_index=True)
        print(f"✅ {len(result)} satır veri alındı.")
        new_entries = []
        for _, row in result.iterrows():
            new_entry = Fund(
                fund_code=row["fundCode"],
                fund_name=row["fundName"],
                price=row["returnByDate"],
                period=row["period"],
                category=row["category"],
            )
            new_entries.append(new_entry)

        # bulk writing
        logging.info(new_entries)
        Fund.objects.bulk_create(new_entries)

        print("Foreign fund data updated successfully.")

        return result
