"""
Stock Collector Scheduler - Basitleştirilmiş Versiyon
Sadece veri toplama işlemi yapar, email/ML yok
"""
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from django.apps import apps
import logging

# Veri toplama modülleri
from stockcollector.data.retrieve_foreign import Stocks
from stockcollector.data.retrieve_bist import StocksBST
from stockcollector.data.retrieve_realtime import StocksRealtime, StockRealtimeCleanup
from stockcollector.data.retrieve_funds import Tefas  # YENİ!


def retrieve_data_bist():
    """BIST hisselerinden günlük veri çek"""
    stocks_app = apps.get_app_config('data')
    stock_obj = StocksBST(stocks_app.name, stocks_app.module)
    stock_obj.run()


def retrieve_data_foreign():
    """Yabancı hisselerinden günlük veri çek"""
    stocks_app = apps.get_app_config('data')  
    stocks_obj = Stocks(stocks_app.name, stocks_app.module)
    stocks_obj.run()


def retrieve_funds():
    """Türk yatırım fonlarından veri çek (TEFAS)"""
    stocks_app = apps.get_app_config('data')
    funds_obj = Tefas(stocks_app.name, stocks_app.module)
    funds_obj.run()


def retrieve_realtime():
    """Real-time (intraday) veri çek - her 30 saniye"""
    stocks_app = apps.get_app_config('data')
    realtime_obj = StocksRealtime(stocks_app.name, stocks_app.module)
    realtime_obj.run()


def cleanup_realtime():
    """Eski real-time veriyi temizle - günde 1 kere"""
    stocks_app = apps.get_app_config('data')
    cleanup_obj = StockRealtimeCleanup(stocks_app.name, stocks_app.module)
    cleanup_obj.run()


def start():
    """Scheduler başlat"""
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), 'default')
    register_events(scheduler)
    
    # ==========================================
    # GÜNLÜK VERİ TOPLAMA (Her gün 1 kere)
    # ==========================================
    
    # BIST verileri - her gün 07:00
    scheduler.add_job(
        retrieve_data_bist,
        trigger=CronTrigger(day_of_week='sat',hour=7, minute=0),
        name='Günlük BIST Veri Toplama',
        id='daily_bist_data',
        replace_existing=True,
    )

    # Foreign verileri - her gün 05:00
    scheduler.add_job(
        retrieve_data_foreign,
        trigger=CronTrigger(day_of_week='sat', hour=1, minute=0),
        name='Günlük Foreign Veri Toplama',
        id='daily_foreign_data',
        replace_existing=True,
    )

    # Fonlar - her hafta cuma 19:00 (TEFAS kapanış sonrası)
    scheduler.add_job(
        retrieve_funds,
        trigger=CronTrigger(day_of_week='fri', hour=19, minute=0),
        name='Haftalık Cuma Fon Veri Toplama',
        id='weekly_fund_data',
        replace_existing=True,
    )

    # ==========================================
    # REAL-TIME VERİ (Sadece borsa saatlerinde)
    # ==========================================
    
    # Real-time veri çekme - her 30 saniye (borsa açıkken)
    # US Market: 14:30-21:00 UTC (09:30-16:00 EST)
    # BIST: 06:30-15:00 UTC (09:30-18:00 Istanbul)
    scheduler.add_job(
        retrieve_realtime,
        trigger=IntervalTrigger(seconds=30),
        name='Real-Time Veri (Her 30sn)',
        id='realtime_stock_data',
        replace_existing=True,
    )
    # Not: Job her 30 saniyede çalışır ama içeride borsa kontrolü var

    # ==========================================
    # TEMİZLİK (Günde 1 kere)
    # ==========================================
    
    # Eski real-time veriyi sil - her gün 02:00
    scheduler.add_job(
        cleanup_realtime,
        trigger=CronTrigger(hour=2, minute=0),
        name='Eski Veri Temizleme',
        id='cleanup_old_data',
        replace_existing=True,
    )
    
    scheduler.start()
    logging.info("✅ Scheduler başlatıldı - Veri toplama aktif")
    logging.info("📊 Günlük veri: 05:00 (Foreign), 07:00 (BIST), 19:00 (Fonlar)")
    logging.info("🔴 Real-time: Her 30 saniye (borsa saatlerinde)")
    logging.info("🧹 Temizlik: Her gün 02:00")

