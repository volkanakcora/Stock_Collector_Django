from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import register_events, DjangoJobStore
from stockcollector.data.retrieve import stocks
from stockcollector.data.email import stock_analytics
from django_apscheduler import util
from django_apscheduler.models import DjangoJobExecution
from apscheduler.triggers.cron import CronTrigger
import logging

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), 'djangojobstore')
    register_events(scheduler)

    @scheduler.scheduled_job('interval', hours=20, name='retrieve_data')
    def retrieve_data():
        from django.apps import apps  # Import apps module
        stocks_app = apps.get_app_config('data')  # Get the app config
        stocks_obj = stocks(stocks_app.name, stocks_app.module)
        stocks_obj.run()
    
    @scheduler.scheduled_job('interval', hours=27, name='send_email')
    def send_email():
        from django.apps import apps  # Import apps module
        email_app = apps.get_app_config('data')  # Get the app config
        email_obj = stock_analytics(email_app.name, email_app.module)
        email_obj.run()
    
    @util.close_old_connections
    def delete_old_job_executions(max_age=604_800):
        """
        This job deletes APScheduler job execution entries older than `max_age` from the database.
        It helps to prevent the database from filling up with old historical records that are no
        longer useful.
        
        :param max_age: The maximum length of time to retain historical job execution records.
                        Defaults to 7 days.
        """
        DjangoJobExecution.objects.delete_old_job_executions(max_age)

    scheduler.add_job(
      delete_old_job_executions,
      trigger=CronTrigger(
        day_of_week="mon", hour="00", minute="00"
      ),  # Midnight on Monday, before start of the next work week.
      id="delete_old_job_executions",
      max_instances=1,
      replace_existing=True,
    )
    logging.info(
      "Added weekly job: 'delete_old_job_executions'."
    )
    scheduler.start()
