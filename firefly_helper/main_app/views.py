from django.shortcuts import render

# Create your views here.
def index(request):
    
    context = {
        'title': 'System Health Checks',
        'iframe_url': 'https://ecommercepanel.com/health-check/',
    }

    template = 'home.html'
    return render(request, template, context)