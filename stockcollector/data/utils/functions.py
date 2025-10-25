from django.conf import settings
import yfinance as yf
from datetime import date, timedelta, datetime
import smtplib
import io
import requests
from io import BytesIO
import logging
import time
import pandas as pd

def get_stock_prices(startDate, endDate, ticker, retries=3, pause=5):
    """
    Hisse senedi OHLCV verilerini yfinance kullanarak indir.
    WORKAROUND: Yahoo Finance rate limiting için optimizasyonlar
    
    Args:
        startDate: Başlangıç tarihi (YYYY-MM-DD)
        endDate: Bitiş tarihi (YYYY-MM-DD)
        ticker: Hisse senedi sembolü (örn: 'AAPL', 'GARAN.IS')
        retries: Deneme sayısı (varsayılan: 3)
        pause: Denemeler arası bekleme süresi saniye (varsayılan: 5)
    
    Returns:
        DataFrame: Open, High, Low, Close, Volume, Date, ticker kolonları
        Hata durumunda boş DataFrame
    """
    # Boş DataFrame şablonu
    empty_df = pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume", "Date", "ticker"])
    
    # Ticker'ı temizle
    ticker = ticker.strip()
    if not ticker:
        logging.error("Ticker boş olamaz")
        return empty_df
    
    # Her deneme için döngü
    for attempt in range(1, retries + 1):
        try:
            if attempt == 1:
                logging.info(f"{ticker} için veri indiriliyor...")
            else:
                logging.debug(f"{ticker} için veri indiriliyor (Deneme {attempt}/{retries})...")
            
            # WORKAROUND 1: Ticker objesi kullan (daha stabil)
            stock = yf.Ticker(ticker)
            
            # WORKAROUND 2: history() metodunu kullan (download() yerine)
            df = stock.history(start=startDate, end=endDate, auto_adjust=True)
            
            # Veri boş mu kontrol et
            if df is None or df.empty:
                if attempt < retries:
                    logging.debug(f"{ticker} için veri bulunamadı, {pause}s bekleniyor...")
                    time.sleep(pause)
                    continue
                else:
                    logging.warning(f"✗ {ticker} - veri bulunamadı")
                    return empty_df
            
            # Index'i sütun olarak ekle (Date)
            df = df.reset_index()
            
            # Kolon isimlerini standartlaştır
            if 'Date' in df.columns:
                pass
            elif 'index' in df.columns:
                df.rename(columns={'index': 'Date'}, inplace=True)
            else:
                logging.error(f"{ticker} için Date kolonu bulunamadı")
                return empty_df
            
            # WORKAROUND 3: Adj Close yerine Close kullan (auto_adjust=True olduğunda)
            # yfinance auto_adjust=True olunca Close zaten adjusted oluyor
            required_cols = ["Open", "High", "Low", "Close", "Volume"]
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                logging.error(f"{ticker} için eksik kolonlar: {missing_cols}")
                return empty_df
            
            # Sadece gerekli kolonları seç
            df = df[["Open", "High", "Low", "Close", "Volume", "Date"]].copy()
            
            # Ticker kolonu ekle
            df["ticker"] = ticker
            
            # NaN kontrolü
            if df[["Open", "High", "Low", "Close"]].isna().all().all():
                logging.warning(f"{ticker} için tüm fiyat verileri NaN")
                return empty_df
            
            logging.info(f"✓ {ticker} için {len(df)} satır veri alındı")
            
            # WORKAROUND 4: Her başarılı request sonrası kısa bekleme (rate limit için)
            time.sleep(1)
            
            return df
            
        except Exception as e:
            error_msg = str(e)
            
            # Rate limit hatası
            if "429" in error_msg or "Too Many Requests" in error_msg:
                wait_time = pause * (attempt + 1)  # Exponential backoff
                logging.warning(f"⚠️  {ticker} - Rate limit, {wait_time}s bekleniyor...")
                time.sleep(wait_time)
                if attempt < retries:
                    continue
            
            # Delisted/Invalid ticker
            if "delisted" in error_msg.lower() or "invalid" in error_msg.lower():
                logging.warning(f"✗ {ticker} - geçersiz ticker veya delisted")
                return empty_df
            
            # JSON decode hatası (Yahoo Finance geçici sorun)
            if "JSONDecodeError" in error_msg or "Expecting value" in error_msg:
                logging.warning(f"⚠️  {ticker} - Yahoo Finance geçici hata, {pause}s bekleniyor...")
                time.sleep(pause)
                if attempt < retries:
                    continue
            
            # Diğer hatalar
            if attempt < retries:
                logging.debug(f"{ticker} hatası, tekrar deneniyor: {error_msg}")
                time.sleep(pause)
            else:
                logging.warning(f"✗ {ticker} - başarısız: {error_msg}")
                return empty_df
    
    return empty_df

def get_day_of_the_month():
    today = date.today()
    return today


def get_yesterday():
    today = get_day_of_the_month()
    yesterday = today - timedelta(days=2)
    return yesterday
