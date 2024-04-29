from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import register_events, DjangoJobStore
from stockcollector.data.retrieve import stocks
from stockcollector.data.email import stock_analytics


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), 'djangojobstore')
    register_events(scheduler)

    @scheduler.scheduled_job('interval', hours=23, name='retrieve_data')
    def retrieve_data():
        from django.apps import apps  # Import apps module
        stocks_app = apps.get_app_config('data')  # Get the app config
        stocks_obj = stocks(stocks_app.name, stocks_app.module)
        stocks_obj.run()
    
    @scheduler.scheduled_job('interval', hours=25, name='send_email')
    def send_email():
        from django.apps import apps  # Import apps module
        email_app = apps.get_app_config('data')  # Get the app config
        email_obj = stock_analytics(email_app.name, email_app.module)
        email_obj.run()
    scheduler.start()
