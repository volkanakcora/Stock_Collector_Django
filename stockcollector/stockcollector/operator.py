from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from stockcollector.data.retrieve_foreign import Stocks
from stockcollector.data.retrieve_bist import StocksBST
from stockcollector.data.send_foreign_weekly import stock_analytics
from stockcollector.data.send_bist_weekly import stock_analytics_bist
from stockcollector.data.send_bist_3_days import stock_analytics_send_bist_3_days
from stockcollector.data.send_bist_daily import stock_analytics_send_bist_daily
from stockcollector.data.send_bist_5_days import stock_analytics_send_bist_5_days
from stockcollector.data.send_foreign_3_days import stock_analytics_send_foreign_3_days
from stockcollector.data.send_foreign_daily import stock_analytics_send_foreign_daily
from stockcollector.data.send_foreign_5_days import stock_analytics_send_foreign_5_days

from stockcollector.data.bist_ML import StocksBSTPredict
from stockcollector.data.foreign_ML import StocksPredict
from django_apscheduler import util
from apscheduler.triggers.cron import CronTrigger
from django.apps import apps
from django_apscheduler.models import DjangoJobExecution
import logging

def send_bist_daily():
    stocks_app = apps.get_app_config('data')
    stock_obj = stock_analytics_send_bist_daily(stocks_app.name, stocks_app.module)
    stock_obj.run()

def send_bist_3_days():
    stocks_app = apps.get_app_config('data')
    stock_obj = stock_analytics_send_bist_3_days(stocks_app.name, stocks_app.module)
    stock_obj.run()

def send_bist_5_days():
    stocks_app = apps.get_app_config('data')
    stock_obj = stock_analytics_send_bist_5_days(stocks_app.name, stocks_app.module)
    stock_obj.run()

def send_foreign_daily():
    stocks_app = apps.get_app_config('data')
    stock_obj = stock_analytics_send_foreign_daily(stocks_app.name, stocks_app.module)
    stock_obj.run()

def send_foreign_3_days():
    stocks_app = apps.get_app_config('data')
    stock_obj = stock_analytics_send_foreign_3_days(stocks_app.name, stocks_app.module)
    stock_obj.run()

def send_foreign_5_days():
    stocks_app = apps.get_app_config('data')
    stock_obj = stock_analytics_send_foreign_5_days(stocks_app.name, stocks_app.module)
    stock_obj.run()

def retrieve_data_bist():
    stocks_app = apps.get_app_config('data')
    stock_obj = StocksBST(stocks_app.name, stocks_app.module)
    stock_obj.run()

def retrieve_data_foreign():
    stocks_app = apps.get_app_config('data')  
    stocks_obj = Stocks(stocks_app.name, stocks_app.module)
    stocks_obj.run()

def send_foreign():
    email_app = apps.get_app_config('data')  
    email_obj = stock_analytics(email_app.name, email_app.module)
    email_obj.run()

def send_bist():
    email_app = apps.get_app_config('data')  
    email_obj = stock_analytics_bist(email_app.name, email_app.module)
    email_obj.run()

def predict_bist():
    stocks_app = apps.get_app_config('data')
    stock_obj = StocksBSTPredict(stocks_app.name, stocks_app.module)
    stock_obj.run()

def predict_foreign():
    stocks_app = apps.get_app_config('data')
    stock_obj = StocksPredict(stocks_app.name, stocks_app.module)
    stock_obj.run()


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), 'default')
    register_events(scheduler)
    
    ##### Monday #####

    ### Prediction Jobs
    scheduler.add_job(
        predict_bist,
        trigger=CronTrigger(hour=10, minute=00, day_of_week='mon'),
        name='precit_data_bist',
        id='predict_data_job_bist',
        replace_existing=True,
    )

    scheduler.add_job(
        predict_foreign,
        trigger=CronTrigger(hour=11, minute=30, day_of_week='mon'),
        name='precit_data_foreign',
        id='predict_data_job_foreign',
        replace_existing=True,
    )
    ### Notification Jobs
    scheduler.add_job(
        send_foreign,
        trigger=CronTrigger(hour=8, minute=40, day_of_week='mon'),
        name='send_data_foreign',
        id='send_data_foreign_job',
        replace_existing=True,
    )

    scheduler.add_job(
        send_bist,
        trigger=CronTrigger(hour=8, minute=45, day_of_week='mon'),
        name='send_data_bist',
        id='send_data_bist_job',
        replace_existing=True,
    )
    ##########################################################################################
    
    # Everyday Jobs
    ### Data Retrive jobs
    scheduler.add_job(
        retrieve_data_foreign,
        trigger=CronTrigger(hour=5, minute=00),
        name='retrieve_data',
        id='retrieve_data_job',
        replace_existing=True,
    )

    scheduler.add_job(
        retrieve_data_bist,
        trigger=CronTrigger(hour=7, minute=20),
        name='retrieve_data_bist',
        id='retrieve_data_job_bist',
        replace_existing=True,
    )
    ### Notification Jobs
    scheduler.add_job(
        send_bist_daily,
        trigger=CronTrigger(hour=10, minute=40),
        name='send_data_bist_daily',
        id='send_data_bist_job_daily',
        replace_existing=True,
    )

    scheduler.add_job(
        send_foreign_daily,
        trigger=CronTrigger(hour=11, minute=50),
        name='send_data_foreign_daily',
        id='send_data_foreign_job_daily',
        replace_existing=True,
    )
    ##################################################################################################

    # WEDNESDAY JOBS
    ### Notification Jobs
    scheduler.add_job(
        send_bist_3_days,
        trigger=CronTrigger(hour=9, minute=45, day_of_week='wed'),
        name='send_data_bist_3_days',
        id='send_data_bist_job_3_days',
        replace_existing=True,
    )

    scheduler.add_job(
        send_foreign_3_days,
        trigger=CronTrigger(hour=9, minute=40, day_of_week='wed'),
        name='send_data_foreign_3_days',
        id='send_data_foreign_job_3_days',
        replace_existing=True,
    )

    ######################################################################################################

    # FRIDAY JOBS
    #NOTIFICATION JOBS
    scheduler.add_job(
        send_bist_5_days,
        trigger=CronTrigger(hour=9, minute=45, day_of_week='fri'),
        name='send_data_bist_5_days',
        id='send_data_bist_job_5_days',
        replace_existing=True,
    )

    scheduler.add_job(
        send_foreign_5_days,
        trigger=CronTrigger(hour=9, minute=40, day_of_week='fri'),
        name='send_data_foreign_5_days',
        id='send_data_foreign_5_days',
        replace_existing=True,
    )
    
    scheduler.start()
    logging.info("Scheduler started.")
