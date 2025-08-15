from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse



def register_view(request):
    context = {}
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect(reverse('home'))
    context['form'] = form
    return render(request, 'accounts/register.html', context)

def login_view(request):
    context = {}
    if request.method == 'POST':
        form = AuthenticationForm(request, data= request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(reverse('home'))
        else:
            context['form'] = form
    else:
        form = AuthenticationForm(request)
        context['form'] = form
    return render(request, 'accounts/login.html', context)

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect(reverse('home'))
    return render(request, 'accounts/logout.html', context= {})