from django.urls import path
from . import views

urlpatterns = [
    path('', views.entrance, name='entrance'),
    path('daily_change', views.LastOneMonth.as_view(), name='daily_change'),
    ]

