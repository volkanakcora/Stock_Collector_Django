from django.apps import AppConfig
from typing import Any
from django.apps import AppConfig as DefaultAppConfig
from django.conf import settings
import logging
import warnings

class AppConfig(DefaultAppConfig):
    name = "stockcollector.data"
    default_auto_field = "django.db.models.BigAutoField"
    # Output confirmations
    warnings.simplefilter(action='ignore', category=FutureWarning)
    logging.basicConfig(level=logging.INFO)

    def run(self):
        raise NotImplementedError("sub classes should implement the run method")

    def ready(self):
        if settings.SCHEDULER_DEFAULT:
            from stockcollector.stockcollector import operator
            operator.start()
