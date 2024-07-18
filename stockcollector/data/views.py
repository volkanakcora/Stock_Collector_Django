from django.shortcuts import render
from .models import Stock
from .models import StockBST
# Create your views here.
from django.http import HttpResponse
from django.views import generic  
from django.db.models import Q
import pandas as pd
from datetime import date
from datetime import date, timedelta

class LastOneMonth(generic.ListView):
    model = Stock
    context_object_name = 'stocks'
    queryset = Stock.objects.all()
    template_name = 'data/daily_change.html'


    def get_context_data(self, **kwargs):
        yesterday = date.today() - timedelta(days=7)
        queryset = Stock.objects.filter(date=yesterday)
        sorted_data = queryset.order_by('-daily_change')[:50] 
        context = super(LastOneMonth, self).get_context_data(**kwargs)
        context['greetings_to'] = 'Anonymous'
        context['num_articles'] = Stock.objects.all().count()
        context['sorted_data'] = sorted_data  

        return context


def entrance(request):
  """
  Renders the index page with a list of news articles grouped by date.
  """
  return render(request, 'data/entrance.html')