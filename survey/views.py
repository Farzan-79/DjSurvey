from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.urls import reverse
from .forms import SurveyCreationForm, SurveyQuestionForm, SurveyTitleForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Survey
# Create your views here.

def survey_detail_view(request, slug=None):
    survey = get_object_or_404(Survey, slug=slug)
    context = {
        'object': survey
    }
    return render(request, 'survey/detail.html', context)
    

@login_required
def survey_creation_view(request):
    form = SurveyTitleForm(request.POST or None)
    if form.is_valid():
        new_survey = form.save(commit=False)
        new_survey.user = request.user
        new_survey.save()
        #### this adds the new survey pk to the session, so in the edit form that comes after this, it is present
        # and it can find out if its a regular edit or a new creation ####
        request.session['new_survey_pk'] = new_survey.pk
        url = reverse('survey:edit', kwargs={'slug': new_survey.slug})
        if request.htmx:
            return HttpResponse('saved', headers={'HX-Redirect': url})
        return redirect(url)

    context = {
        'form': form,
        'create': True,
    }
    if request.htmx: #if its invalid, only render the partial
        return render(request, 'survey/create/par-create-title.html', context)
    #initial render, the full page
    return render(request,'survey/create/create-title.html', context)
    
def survey_edit_view(request, slug=None):
    survey_object = get_object_or_404(Survey, slug=slug, user=request.user)
    form= SurveyCreationForm(request.POST or None, instance= survey_object)
    #### i set .get instead of .pop because if its pop, it will no longer be present in the POST method. so i want to set this value, and keep the session value for later
    created_pk = request.session.get('new_survey_pk', None)
    context = {
        'form': form,
        'object': survey_object,
        'create': survey_object.pk == created_pk,
    }
    
    if form.is_valid():
        #### here i just pop it so it is deleted, i had to keep it until this part, after that it should no longer be present
        created_pk = request.session.pop('new_survey_pk', None)
        form.save()
        if request.htmx:
            return render(request, 'survey/create/saved.html', context)
        return redirect(reverse('survey:detail', kwargs={'slug': survey_object.slug}))

    if request.htmx:  #if its invalid, only render the partial
        return render(request, 'survey/create/par-edit.html', context)
    #initial render, the full page
    return render(request, 'survey/create/edit.html', context)

@login_required
def survey_delete_view(request, slug=None):
    object= get_object_or_404(Survey, slug=slug, user= request.user)
    context = {
        'object': object
    }

    if request.method == 'POST':
        object.delete()
        succes_url = reverse('accounts:profile')
        if request.htmx:
            return HttpResponse('success', headers= {'HX-Redirect': succes_url})
        return redirect(succes_url)
    
    if request.htmx:
        return render(request, 'survey/create/par-survey-delete.html', context)
    return render(request, 'survey/create/survey-delete.html', context)



    

    
