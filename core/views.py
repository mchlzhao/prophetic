from django.contrib.auth.decorators import login_required
from django.shortcuts import render

def home(request):
    return render(request, 'core/home.html')

@login_required
def markets(request):
    return render(request, 'core/markets.html')