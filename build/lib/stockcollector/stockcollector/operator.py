from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from stockcollector.data.retrieve_foreign import Stocks
from stockcollector.data.retrieve_bist import StocksBST
from stockcollector.data.send_foreign import stock_analytics
from stockcollector.data.send_bist import stock_analytics_bist

from django_apscheduler import util
from apscheduler.triggers.cron import CronTrigger
from django.apps import apps
from django_apscheduler.models import DjangoJobExecution
import logging

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

# @util.close_old_connections
# def delete_old_job_executions(max_age=604_800):
#     DjangoJobExecution.objects.delete_old_job_executions(max_age)

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), 'default')
    register_events(scheduler)

    scheduler.add_job(
        retrieve_data_foreign,
        trigger=CronTrigger(hour=6, minute=00),  # Every day at 20:00
        name='retrieve_data',
        id='retrieve_data_job',
        replace_existing=True,
    )

    scheduler.add_job(
        retrieve_data_bist,
        trigger=CronTrigger(hour=7, minute=40),  # Every day at 20:00
        name='retrieve_data_bist',
        id='retrieve_data_job_bist',
        replace_existing=True,
    )

    scheduler.add_job(
        send_foreign,
        trigger=CronTrigger(hour=8, minute=00),  # Every day at 10:00
        name='send_data_foreign',
        id='send_data_foreign_job',
        replace_existing=True,
    )

    scheduler.add_job(
        send_bist,
        trigger=CronTrigger(hour=8, minute=2),  # Every day at 10:00
        name='send_data_foreign_bist',
        id='send_data_foreign_bist_job',
        replace_existing=True,
    )
    
    scheduler.start()
    logging.info("Scheduler started.")
