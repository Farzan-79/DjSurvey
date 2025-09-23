from django.shortcuts import render, redirect, get_object_or_404, HttpResponse 
from django.urls import reverse
from django.http import Http404
from django.db import transaction
from .forms import SurveyCreationForm, QuestionForm, SurveyTitleForm, ChoiceForm, ChoiceFormSet
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Survey, Question, Answer, Choice
from .utils import generate_stable_prefix, generate_temp_prefix

#? ------------------------------------------------------------------------
#? Views for the survey app.
#? ------------------------------------------------------------------------
#? High-level map:
#? - survey_creation_view  -> create survey title, then redirect to survey_edit_view
#? - survey_edit_view      -> edit survey description and manage questions (uses HTMX)
#? - question_create_view  -> HTMX endpoint: show/save a new question (uses temp prefix for formset)
#? - question_update_view  -> HTMX endpoint: edit/save an existing question (stable prefix based on id)
#? - choice_area_view      -> HTMX endpoint: returns choice formset HTML for a question
#?
#? The trickiest pieces: prefixes for the ChoiceFormSet and using HTMX to swap only small parts.
#? Prefix ensures the formset fields' names match between client and server so Django binds them correctly.
#? ------------------------------------------------------------------------


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
        #? store created PK in session so edit view knows this is immediate post-create (used to show "create" indicator)
        request.session['new_survey_pk'] = new_survey.pk
        url = reverse('survey:edit', kwargs={'slug': new_survey.slug})
        if request.htmx:
            #* If the request came from HTMX, send HX-Redirect header. HTMX will follow it.
            return HttpResponse('saved', headers={'HX-Redirect': url})
        return redirect(url)

    context = {
        'form': form,
        'create': True,
    }
    if request.htmx:
        #* When HTMX triggered the POST and validation failed, only the partial should be re-rendered
        return render(request, 'survey/create/par-create-title.html', context)
    #* initial render, the full page
    return render(request,'survey/create/create-title.html', context)
    
def survey_edit_view(request, slug=None):
    survey_obj = get_object_or_404(Survey, slug=slug, user=request.user)
    form= SurveyCreationForm(request.POST or None, instance= survey_obj)
    #? i set .get instead of .pop because if its pop, it will no longer be present in the POST method.
    #? so i want to set this value, and keep the session value for later (only pop it on successful save)
    created_pk = request.session.get('new_survey_pk', None)
    context = {
        'survey_form': form,
        'survey_obj': survey_obj,
        #? boolean used by template to show "create" vs "edit"
        'create': survey_obj.pk == created_pk,
    }
    
    if form.is_valid():
        #? here i just pop it so it is deleted, i had to keep it until this part, after that it should no longer be present
        created_pk = request.session.pop('new_survey_pk', None)
        form.save()
        if request.htmx:
            #* render a small saved tile partial for HTMX instead of full redirect (keeps SPA-like behaviour)
            return render(request, 'survey/create/saved.html', context)
        #* a regular page to redirect to if HTMX was not working (never)
        return redirect(reverse('survey:detail', kwargs={'slug': survey_obj.slug}))

    if request.htmx:  #* if its invalid, only render the partial
        return render(request, 'survey/create/par-edit.html', context)
    #* initial render, the full page
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
    #? Simple read-only partial. Used to render existing question summary (par-question.html).
    try:
        parent_survey = Survey.objects.get(slug=parent_slug)
    except:
        parent_survey = None
    if parent_survey == None:
        return HttpResponse("Survey not found")
    
    #* checking if this question was there before, or we are creating a new one
    try:
        instance = Question.objects.get(survey=parent_survey, id=id)
    except:
        instance = None

    context = {
        'question_obj': instance
    }
    return render(request, 'survey/create/par-question.html', context)


def question_create_view(request, parent_slug=None):
    #? --------------------------------------------------------------------
    #? Create a new question for a survey.
    #? - Uses a temporary prefix for unsaved forms (generate_temp_prefix()).
    #? - On POST: reads the client's prefix so posted choice fields bind correctly.
    #? - On success (HTMX) returns display partial (par-question.html).
    #? - On validation error re-renders the form partial with same prefix so user input is preserved.
    #? --------------------------------------------------------------------

    parent_survey = get_object_or_404(Survey, slug=parent_slug)

    #? prefix handling:
    #? - When the client first loads the create form (GET), there is no prefix in POST, so generate_temp_prefix()
    #? - When the client later posts we expect the client to include 'prefix' hidden input. That allows subsequent
    #?   HTMX sub-requests (add choice) to reference the same prefix.
    prefix = request.POST.get('prefix') or generate_temp_prefix()

    #* The question_form doesn't have an instance because this is creation.
    question_form = QuestionForm(request.POST or None)
    #* Provide prefix even on GET so we render inputs with stable names (choice-<something>-0-title)
    choice_formset = ChoiceFormSet(request.POST or None, instance=None, prefix=prefix)

    context = {
        'question_form': question_form,
        'choice_formset': choice_formset,
        'survey_obj': parent_survey,
        'prefix': prefix
    }

    if question_form.is_valid():
        #* If question type is multiple_choice then we also must validate/save the choices (formset)
        if question_form.cleaned_data.get('question_type') == 'multiple_choice':
            if choice_formset.is_valid():
                with transaction.atomic():
                    #* Save question first, then attach the saved question instance to the formset and save choices.
                    question = question_form.save(commit=False)
                    question.survey = parent_survey
                    question.save()
                    choice_formset.instance = question
                    choice_formset.save()
                #* On success return the rendered question partial (display mode)
                return render(request, 'survey/create/par-question.html', {'question_obj':question})
            #* If choices invalid, re-render the question form partial with the same prefix (so user input isn't lost)
            return render(request, 'survey/create/par-question-form.html', context=context)
        else:
            #* Text question — just save the question and return display partial
            question = question_form.save(commit=False)
            question.survey = parent_survey
            question.save()
            return render(request, 'survey/create/par-question.html', {'question_obj':question})
    #* initial GET or invalid form: render the question form partial (with prefix)
    return render(request, 'survey/create/par-question-form.html', context=context)


def question_update_view(request, parent_slug=None, id=None):
    #? --------------------------------------------------------------------
    #? Edit an existing question.
    #? - Uses stable prefix (choice-<id>) by default, but accepts a posted prefix if the client includes one.
    #? - Saves question and choice formset atomically if valid.
    #? - Deletes choices if type switched to text.
    #? --------------------------------------------------------------------

    # checking if there is a parent survey for the question. it must have it
    parent_survey = get_object_or_404(Survey, slug=parent_slug)
    # checking if this question was there before, or we are creating a new one
    instance = get_object_or_404(Question, survey=parent_survey, id=id)

    #? prefix selection logic:
    #? - prefer a prefix posted by the client (this allows client to use a temp prefix while editing without touching DB)
    #? - otherwise use stable prefix derived from id (generate_stable_prefix(instance.id)), e.g. "choice-51"
    prefix = request.POST.get('prefix') or generate_stable_prefix(instance.id)

    #* Bind POST to the forms so they can validate/save
    question_form = QuestionForm(request.POST or None, instance= instance)
    choice_formset = ChoiceFormSet(request.POST or None, instance= instance, prefix=prefix)

    context = {
        'question_form': question_form,
        'question_obj': instance,
        'survey_obj': parent_survey,
        'choice_formset': choice_formset,
        'prefix': prefix,
    }
    
    if question_form.is_valid():
        if question_form.cleaned_data.get('question_type') == 'multiple_choice':
            if choice_formset.is_valid():
                with transaction.atomic():
                    #* Save the question and the related choices. choice_formset.instance assigned in constructor + again for clarity.
                    question = question_form.save()
                    choice_formset.instance = question
                    choice_formset.save()
                return render(request, 'survey/create/par-question.html', {'question_obj':question})
            #* if formset invalid: re-render the form partial to show errors using same prefix (so data persists)
            return render(request, 'survey/create/par-question-form.html', context)
        else: #* meaning the question type is text
            question = question_form.save()

        #* This ensures a question switched from multiple_choice to text will not keep stale choice objects.
        if question.question_type == 'text' and question.choices.exists():
            question.choices.all().delete()
        return render(request, 'survey/create/par-question.html', {'question_obj':question})

    #* GET or invalid question_form -> re-render the form partial (choice formset present if multiple_choice)
    return render(request, 'survey/create/par-question-form.html', context)


def question_delete_view(request, parent_slug=None, id=None):
    if not request.htmx:
        raise Http404
    
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
def choice_area_view(request, parent_slug=None):
    #? ------------------------------------------------------------------------
    #? HTMX endpoint responsible for rendering the "choice area" partial:
    #? - Renders ChoiceFormSet partial (par-choice-area.html).
    #? - Accepts POST with action=add to append a blank form (increase TOTAL_FORMS).
    #? - Uses 'prefix' to bind posted data to correct formset names.
    #?
    #? Routes that call this:
    #? - par-question-form.html on `hx-trigger="change"` of question_type select
    #? - par-choice-area's "+ Add choice" button posts here with hx-vals action=add
    #?
    #? Returns blank response if question_type != 'multiple_choice'
    #? Important: this endpoint must include management_form & hidden fields for every form so that
    #? the parent form POST later will contain the correct hidden ids.
    #? ------------------------------------------------------------------------

    parent_survey = get_object_or_404(Survey, slug=parent_slug)

    #? prefix ordering: prefer POST (client included), then GET, fallback to literal 'choice'
    prefix = request.POST.get('prefix') or request.GET.get('prefix') or 'choice'

    question_obj = None
    #? id may be present when editing an existing question (so show existing choices). For new questions, id is None.
    q_id = request.POST.get('id') or request.GET.get('id') or None
    if q_id is not None:
        #* filter by survey to avoid cross-survey leaks
        question_obj = Question.objects.filter(id=q_id, survey=parent_survey).first()

    #? Determine question_type either from posted form_type or from existing question_obj.
    question_type = request.POST.get('question_type') or (question_obj.question_type if question_obj else None)

    if question_type == 'multiple_choice':
        if request.method == 'POST':
            #* We copy POST so we can mutate TOTAL_FORMS when action=add
            data = request.POST.copy()
            action = data.get('action')

            if action == 'add':
                #? The client asked to add a blank form. Increase TOTAL_FORMS by 1 so the returned HTML contains one more form.
                total_key = f'{prefix}-TOTAL_FORMS'
                raw_current_total = data.get(total_key, 0)
                try:
                    current_total = int(raw_current_total)
                except (ValueError, TypeError):
                    #! guard: sometimes the field can be empty string; fallback to 0
                    current_total = 0
                new_total = current_total+1
                data[total_key] = str(new_total)
                #* construct formset bound to mutated data so template shows one more blank form
                choice_formset = ChoiceFormSet(data, instance=question_obj, prefix=prefix)
            else:
                #* No special action: render formset for the question (bound to POST if present)
                choice_formset = ChoiceFormSet(instance=question_obj, prefix=prefix)
        else:
            #* GET: return unbound formset for question or empty formset (if question_obj is None)
            choice_formset = ChoiceFormSet(instance=question_obj, prefix=prefix)
    
    else:
        #* Not multiple_choice -> nothing to render in choice area
        return HttpResponse('')

    context = {
        'choice_formset': choice_formset,
        'question_obj': question_obj,
        'prefix': prefix,
        'survey_obj': parent_survey
    }

    return render(request, 'survey/create/par-choice-area.html', context=context)
