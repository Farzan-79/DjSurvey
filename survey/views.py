from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .forms import SurveyCreationForm, SurveyQuestionForm, SurveyTitleForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Survey
# Create your views here.

def survey_detail_view(request, slug=None):
    survey = get_object_or_404(Survey, slug=slug)
    context = {
        'survey': survey
    }
    return render(request, 'survey/detail.html', context)
    

@login_required
def survey_creation_view(request):
    form = SurveyTitleForm(request.POST or None)
    if form.is_valid():
        new_survey = form.save(commit=False)
        new_survey.user = request.user
        new_survey.save()
        new_context={
            'object': new_survey,
            'form': SurveyCreationForm(instance= new_survey),
            'create': True,
        }
        if request.htmx:
            return render(request, 'survey/create/par-edit.html', new_context)
        return redirect(reverse('survey:edit', kwargs={'slug': new_survey.slug}))

    context = {
        'form': form,
        'create': True,
    }
    if request.htmx:
        return render(request, 'survey/create/par-create-title.html', context)
    return render(request,'survey/create/create-update.html', context)
    
def survey_edit_view(request, slug=None):
    survey_object = get_object_or_404(Survey, slug=slug)
    form= SurveyCreationForm(request.POST or None, instance= survey_object)
    context = {
        'form': form,
        'edit': True,
        'object': survey_object
    }
    if form.is_valid():
        form.save()
        if request.htmx:
            return render(request, 'survey/create/saved.html', context)
        return redirect(reverse('survey:detail', kwargs={'slug': survey_object.slug}))    
    if request.htmx:
        return render(request, 'survey/create/par-edit.html', context)
    return render(request, 'survey/create/create-update.html', context)


#def survey_edit_view(request, slug=None):
#    survey = get_object_or_404(Survey, slug=slug)
#    survey_form = SurveyCreationForm(request.POST or None, instance=survey)
#    questions = survey.questions.all()
#    for q in questions:
#        question_form = SurveyQuestionForm(request.POST or None, instance=q)
#    empty_question_form = SurveyQuestionForm(request.POST or None)
#    context = {
#        'form_s': survey_form,
#        'form_q': empty_question_form
#    }
#    if survey_form.is_valid() and empty_question_form.is_valid():
#        s = survey_form.save(commit=False)
#        q = empty_question_form.save(commit=False)
#        q.survey = survey
#        q.save()
#        s.save()
#        return redirect(reverse('survey:detail', kwargs={'slug': slug}))
#    return render(request, 'survey/create/edit.html', context)

    

    
