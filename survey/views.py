from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .forms import SurveyCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
def survey_creation_view(request):
    form = SurveyCreationForm(request.POST or None)
    if form.is_valid():
        new_survey = form.save(commit=False)
        new_survey.user = request.user
        new_survey.save()
        return redirect(reverse('home'))
    else:
        context = {
            'form': form
        }
        return render(request,'survey/create/create-title.html', context) 
