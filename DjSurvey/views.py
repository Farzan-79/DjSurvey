from django.shortcuts import render
from django.http import HttpResponse

def home_view(request):
    context = {}
    return render(request, 'home-view.html', context=context)