from django.db import models

# Create your models here.

from django.db import models


class Stock(models.Model):
    date = models.DateTimeField(null=True, blank=True)
    open_price = models.FloatField(null=True, blank=True)  # Renamed for clarity
    high_price = models.FloatField(null=True, blank=True)  # Renamed for clarity
    low_price = models.FloatField(null=True, blank=True)  # Renamed for clarity
    close_price = models.FloatField(null=True, blank=True)  # Renamed for clarity
    adjusted_close = models.FloatField(null=True, blank=True)  # Changed to snake_case
    volume = models.FloatField(null=True, blank=True)
    stock_name = models.CharField(max_length=255)  # Specify max length
    # Remove count (primary key should be auto-incrementing integer)
    daily_return = models.FloatField(null=True, blank=True)  # Renamed for clarity
    volatility = models.FloatField(null=True, blank=True)
    daily_change = models.FloatField(null=True, blank=True)  # Renamed for clarity
    high_low_spread = models.FloatField(null=True, blank=True)
    expected_change = models.FloatField(null=True, blank=True)  # Renamed for clarity
    magnitude = models.FloatField(null=True, blank=True)
    context = models.FloatField(null=True, blank=True)

    
    class Meta:
        app_label = 'data'
        verbose_name = 'child'
