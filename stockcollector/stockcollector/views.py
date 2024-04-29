from django.http import HttpResponse
from django.shortcuts import render 



def home_view(request):
    """
    Improved home page view for your Django app.
    """

    context = {
        'app_name': 'Stock Analytics Application',  # Replace with your app's name
        'links': [
            {'name': 'data', 'url': '/data/'},  # Replace with link details
            {'name': 'being developed', 'url': '/sub_app2/'},  # ... add more links as needed
        ],
        'background_color': '#f0f0f0',  # Customizable background color (optional)
    }

    return render(request, 'home.html', context)