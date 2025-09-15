from django.shortcuts import render, redirect, get_object_or_404, HttpResponse 
from django.urls import reverse
from django.http import Http404
from django.db import transaction
from .forms import SurveyCreationForm, QuestionForm, SurveyTitleForm, ChoiceForm, ChoiceFormSet
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Survey, Question, Answer, Choice
# Create your views here.

def survey_detail_view(request, slug=None):
    survey = get_object_or_404(Survey, slug=slug)
    context = {
        'survey_obj': survey
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
    survey_obj = get_object_or_404(Survey, slug=slug, user=request.user)
    form= SurveyCreationForm(request.POST or None, instance= survey_obj)
    #### i set .get instead of .pop because if its pop, it will no longer be present in the POST method. so i want to set this value, and keep the session value for later
    created_pk = request.session.get('new_survey_pk', None)
    context = {
        'survey_form': form,
        'survey_obj': survey_obj,
        'create': survey_obj.pk == created_pk,
    }
    
    if form.is_valid():
        #### here i just pop it so it is deleted, i had to keep it until this part, after that it should no longer be present
        created_pk = request.session.pop('new_survey_pk', None)
        form.save()
        if request.htmx:
            return render(request, 'survey/create/saved.html', context)
        return redirect(reverse('survey:detail', kwargs={'slug': survey_obj.slug}))

    if request.htmx:  #if its invalid, only render the partial
        return render(request, 'survey/create/par-edit.html', context)
    #initial render, the full page
    return render(request, 'survey/create/edit.html', context)

@login_required
def survey_delete_view(request, slug=None):
    object= get_object_or_404(Survey, slug=slug, user= request.user)
    context = {
        'survey_obj': object
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

def question_view(request, parent_slug=None, id=None):
    try:
        parent_survey = Survey.objects.get(slug=parent_slug)
    except:
        parent_survey = None
    if parent_survey == None:
        return HttpResponse("Survey not found")
    
    # checking if this question was there before, or we are creating a new one
    try:
        instance = Question.objects.get(survey=parent_survey, id=id)
    except:
        instance = None

    context = {
        'question_obj': instance
    }
    return render(request, 'survey/create/par-question.html', context)


def question_create_view(request, parent_slug=None, id=None):
    # checking if there is a parent survey for the question. it must have it
    try:
        parent_survey = Survey.objects.get(slug=parent_slug)
    except:
        parent_survey = None
    if parent_survey == None:
        return HttpResponse("Survey not found")
    
    # checking if this question was there before, or we are creating a new one
    try:
        instance = Question.objects.get(survey=parent_survey, id=id)
    except:
        instance = None

    #url = 

    question_form = QuestionForm(request.POST or None, instance= instance)
    choice_formset = ChoiceFormSet(request.POST or None, instance= instance, prefix='choice')

    context = {
        'question_form': question_form,
        'question_obj': instance,
        'survey_obj': parent_survey,
        'choice_formset': choice_formset,
    }
    
    if question_form.is_valid():
        if instance and question_form.cleaned_data.get('question_type') == 'multiple_choice' and choice_formset.is_valid():
            with transaction.atomic():
                question = question_form.save(commit=False)
                if not instance:
                    question.survey = parent_survey
                question_form.save()
                choice_formset.instance = question
                choice_formset.save()
        else:
            question = question_form.save(commit=False) #if being created for the first time, or it has text as type
            if not instance:
                question.survey = parent_survey
            question_form.save()
        #delete every choice the question might have if type is changed to text
        if question.question_type == 'text' and question.choices.exists():
            for c in question.choices.all():
                c.delete()
        return render(request, 'survey/create/par-question.html', {'question_obj':question})

    return render(request, 'survey/create/par-question-form.html', context)

def question_delete_view(request, parent_slug=None, id=None):
    if not request.htmx:
        return Http404
    
    try:
        parent_survey = Survey.objects.get(slug=parent_slug)
    except:
        parent_survey = None
    if parent_survey == None:
        return HttpResponse("Survey not found")
    
    try:
        instance = Question.objects.get(survey=parent_survey, id=id)
    except:
        instance = None
    if not instance:
        return HttpResponse("Question not found")
    
    
    if request.method=='POST':
        instance.delete()
        return HttpResponse("") # with hx-target="#q-<id>" and outerHTML, this empties it
    
    return render(request, 'survey/create/par-question-delete.html', {'question_obj': instance})

#### used this first, then decided not to use it. we'll see
def choice_create_view(request, q_id=None, c_id= None):
    try:
        parent_question = Question.objects.get(id=q_id)
    except:
        return HttpResponse("question not found") 
    try:
        choice = Choice.objects.get(id=c_id, question=parent_question)
    except:
        choice = None
       
    form = ChoiceForm(request.POST or None, instance= choice)
    if form.is_valid():
        choice = form.save(commit=False)
        if not choice.pk:
            choice.question = parent_question
        choice.save()
        return HttpResponse("Choice saved")
    context = {
        "question_obj": parent_question,
        "choice_form": form,
        "choice_obj": choice,
    }
    return render(request, 'survey/create/par-choice-form.html', context=context)

    






    

    
