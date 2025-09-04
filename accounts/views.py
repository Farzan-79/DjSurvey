from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse
from django.contrib import messages
from .forms import profile_completion_form
from .models import UserProfile



def register_view(request):
    context = {}
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect(reverse('accounts:login'))
    context['form'] = form
    return render(request, 'accounts/register.html', context)

def login_view(request):
    if request.user.is_authenticated:
        messages.info(request, f'You are already logged in, {request.user.username}!')
        return redirect(reverse('accounts:profile'))
    context = {}
    next_url = request.GET.get('next') or request.POST.get('next') # for getting the ?next anytime
    if request.method == 'POST':
        form = AuthenticationForm(request, data= request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if next_url:
                return redirect(next_url)
            return redirect(reverse('accounts:profile'))
        else:
            context['form'] = form
    else:
        form = AuthenticationForm(request)
        context['form'] = form
        if 'next' in request.GET:
            messages.info(request, 'You need to be logged in in order to create a survey')
    return render(request, 'accounts/login.html', context)

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect(reverse('home'))
    if request.htmx:
        return render(request, 'accounts/partials/par-logout.html', context= {})
    return render(request, 'accounts/logout.html', context= {})

def profile_view(request):
    if request.user.is_authenticated:
        context = {
            'profile': request.user.profile,
            'user': request.user
        }
    else:
        login_url = reverse('accounts:login') + '?next=' + reverse('account:profile')
        return redirect(login_url)
    
    return render(request, 'accounts/profile.html', context)

def profile_completion_view(request):
    try:
        profile_obj = get_object_or_404(UserProfile, user = request.user)
    except:
        profile_obj = None
    form = profile_completion_form(request.POST or None, instance=profile_obj)
    if form.is_valid():
        profile = form.save(commit=False)
        if not profile.user:
            profile.user = request.user
        profile.save()
        messages.success(request, "your profile was successfully updated!")
        return redirect(reverse('accounts:profile'))
    return render(request, 'accounts/profile-completion.html', {'form': form})