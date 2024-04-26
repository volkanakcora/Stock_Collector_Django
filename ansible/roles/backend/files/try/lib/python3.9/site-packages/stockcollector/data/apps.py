from django.apps import AppConfig
from typing import Any
from django.apps import AppConfig as DefaultAppConfig
from django.conf import settings


class AppConfig(DefaultAppConfig):
    name = "stockcollector.data"
    default_auto_field = "django.db.models.BigAutoField"

    def run(self):
        raise NotImplementedError("sub classes should implement the run method")

    def ready(self):
        if settings.SCHEDULER_DEFAULT:
            from stockcollector.stockcollector import operator
            operator.start()
