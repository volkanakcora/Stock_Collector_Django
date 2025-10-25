"""
Real-Time Stock Data Collector
Her 30 saniyede bir çalışır ve son dakikanın fiyatlarını çeker
Grafana için optimize edilmiş
"""
import datetime
from django.conf import settings
from .models import StockRealtime
import yfinance as yf
import logging
from django.apps import AppConfig
from django.utils import timezone

class StocksRealtime(AppConfig):
    """Real-time veri çekme (her 30 saniye)"""
    
    def __init__(self, app_name: str, app_module: None) -> None:
        super().__init__(app_name, app_module)

    def run(self):
        try:
            self.retrieve_realtime_data()
        except Exception as e:
            logging.warning(f"Realtime process failed: {str(e)}")

    def retrieve_realtime_data(self):
        """Son dakikanın fiyatlarını çek (intraday) ve PostgreSQL'e kaydet"""
        from datetime import datetime
        import pytz
        
        # Şu anki UTC saati
        now_utc = datetime.now(pytz.UTC)
        hour_utc = now_utc.hour
        
        # Borsa saatleri kontrolü
        # NYSE/NASDAQ: 14:30-21:00 UTC (09:30-16:00 EST)
        # BIST: 06:30-15:00 UTC (09:30-18:00 Istanbul)
        
        is_us_market_open = 14 <= hour_utc < 21  # 14:30-21:00
        is_bist_market_open = 6 <= hour_utc < 15  # 06:30-15:00
        
        if not (is_us_market_open or is_bist_market_open):
            logging.info(f"⏰ Borsalar kapalı (UTC: {hour_utc:02d}:00). US: 14:30-21:00, BIST: 06:30-15:00")
            return []
        
        if (is_us_market_open or is_bist_market_open):
            logging.info("🔴 LIVE: Real-time veri çekiliyor...")
            return []
        
       
        # Watchlist - hangi borsalar açıksa ona göre seç
        watchlist = []
        if is_us_market_open:
            watchlist.extend(['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'])
            logging.info("🇺🇸 US Market açık")
        if is_bist_market_open:
            watchlist.extend(['GARAN.IS', 'THYAO.IS', 'AKBNK.IS', 'TUPRS.IS', 'SASA.IS'])
            logging.info("🇹🇷 BIST açık")

        if not watchlist:
            logging.info("⏰ Hiçbir borsa açık değil")
            return []

        new_entries = []
        success_count = 0
        fail_count = 0

        for symbol in watchlist:
            try:
                # Son 1 günün 1 dakikalık verisi
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1d", interval="1m")

                if not hist.empty:
                    # En son fiyat
                    latest = hist.iloc[-1]
                    timestamp = hist.index[-1]
                    
                    # Günlük değişim hesapla
                    day_open = hist['Close'].iloc[0]
                    change_percent = ((latest['Close'] - day_open) / day_open) * 100
                    
                    # Model objesi oluştur
                    new_entry = StockRealtime(
                        timestamp=timestamp,
                        stock_name=symbol,
                        price=latest['Close'],
                        volume=latest['Volume'],
                        change_percent=change_percent
                    )
                    new_entries.append(new_entry)
                    success_count += 1
                    
                    logging.info(f"✅ {symbol}: ${latest['Close']:.2f} ({change_percent:+.2f}%)")
                else:
                    fail_count += 1
                    logging.warning(f"⚠️ {symbol}: veri yok")

            except Exception as e:
                fail_count += 1
                logging.error(f"❌ {symbol}: {str(e)}")

        # PostgreSQL'e toplu kaydet
        if new_entries:
            StockRealtime.objects.bulk_create(new_entries)
            logging.info(f"💾 {len(new_entries)} kayıt veritabanına eklendi")
        
        logging.info(f"🔴 LIVE: ✅ {success_count} | ❌ {fail_count}")
        return new_entries


class StockRealtimeCleanup(AppConfig):
    """Eski real-time veriyi temizle (günde 1 kere)"""
    
    def run(self):
        """24 saatten eski real-time veriyi sil"""
        from django.utils import timezone
        
        # 24 saatten eski kayıtları sil
        cutoff_time = timezone.now() - datetime.timedelta(hours=24)
        deleted_count = StockRealtime.objects.filter(timestamp__lt=cutoff_time).delete()[0]
        
        logging.info(f"🧹 {deleted_count} eski real-time kayıt silindi")
