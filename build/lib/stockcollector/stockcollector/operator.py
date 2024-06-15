from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from stockcollector.data.retrieve import stocks
from stockcollector.data.email import stock_analytics
from django_apscheduler import util
from apscheduler.triggers.cron import CronTrigger
from django.apps import apps
from django_apscheduler.models import DjangoJobExecution
import logging

def retrieve_data():
    stocks_app = apps.get_app_config('data')  
    stocks_obj = stocks(stocks_app.name, stocks_app.module)
    stocks_obj.run()

def send_email():
    email_app = apps.get_app_config('data')  
    email_obj = stock_analytics(email_app.name, email_app.module)
    email_obj.run()

# @util.close_old_connections
# def delete_old_job_executions(max_age=604_800):
#     DjangoJobExecution.objects.delete_old_job_executions(max_age)

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), 'default')
    register_events(scheduler)

    scheduler.add_job(
        retrieve_data,
        trigger=CronTrigger(hour=18, minute=34),  # Every day at 20:00
        name='retrieve_data',
        id='retrieve_data_job',
        replace_existing=True,
    )

    scheduler.add_job(
        send_email,
        trigger=CronTrigger(hour=19, minute=00),  # Every day at 10:00
        name='send_email',
        id='send_email_job',
        replace_existing=True,
    )

    # scheduler.add_job(
    #     delete_old_job_executions,
    #     trigger=CronTrigger(day_of_week='mon', hour=0),  # Midnight on Monday
    #     id="delete_old_job_executions",
    #     replace_existing=True,
    # )
    
    scheduler.start()
    logging.info("Scheduler started.")
