from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from .models import Survey, Question, Choice, Answer
from django.core.exceptions import ValidationError


class SurveyTitleForm(forms.ModelForm):
    class Meta:
        model= Survey
        fields= ['title'] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['title'].label = 'Title'
        self.fields['title'].widget.attrs.update({
            "placeholder": "Your Survey Name",
            "class": "form-control"
        })


class SurveyCreationForm(forms.ModelForm):
    class Meta:
        model= Survey
        fields= ['description'] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['description'].label = "Description"
        self.fields['description'].widget.attrs.update({
            "placeholder": "Extra information about your survey",
            "rows": "3",
            "class": "form-control"
        })

class QuestionForm(forms.ModelForm):
    class Meta:
        model= Question
        fields = ['title', 'question_type']

    def __init__(self, *args, **kwargs):
        #? we need to have unique IDs for form fields in the template, so:
        #? Widget id strategy:
        #? - If the form has an instance with a pk, use that (stable id): e.g. "51"
        #? - Otherwise, allow caller to pass uid=prefix (e.g. "choice-new-x1")
        #? - Fallback to 'new' if nothing provided (still unique-ish)
        #? This ensures both title and question_type will share the same suffix,
        #? so labels and inputs match and there are no duplicate ids on the page.

        #* uid is passed from the create view to the form, so when ID is none, we get the temp prefix from the view to put in the form id fields
        uid = kwargs.pop('uid', None)
        super().__init__(*args, **kwargs)
        
        if self.instance and getattr(self.instance, 'id', None):
            suffix = str(self.instance.id)
        elif uid:
            suffix = str(uid)
        else:
            suffix = 'new' #* last resort 
            

        #
        self.fields['title'].label= 'Question Title'
        self.fields['title'].widget.attrs.update({
            "placeholder": "e.g. What\'s your favorite color?",
            "class": "form-control",
            "id": f'id_title-{suffix}' #* here we use suffix that was decided above, in the field's id
        })

        self.fields['question_type'].label = "Question Type"
        self.fields['question_type'].widget.attrs.update({
            "class": "form-control",
            "id": f'id_question_type-{suffix}' #* here we use suffix that was decided above, in the field's id
        })

#? ------------------------------------------------------------------------
#? ChoiceForm
#? - Simple ModelForm for Choice
#? - We implement clean_title to normalize whitespace so "   " becomes ""
#? ------------------------------------------------------------------------
class ChoiceForm(forms.ModelForm):
    class Meta:
        model= Choice
        fields = ['title']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label= 'Choice'
        self.fields['title'].widget.attrs.update({
            'placeholder': "e.g. \'Blue\'",
            "class": "form-control"  
        })
    
     #? Field-level cleaning:
        #? - Pull the raw cleaned value from cleaned_data (or default to '').
        #? - Use isinstance(..., str) to be safe before calling .strip() (prevents errors
        #?   if some validator or widget produced a non-strange value).
        #? - Return the stripped value. If the user typed only spaces, this becomes ''.
        #*
        #* Why here:
        #* - Doing trimming at field-level ensures all subsequent formset logic sees normalized text. 
    def clean_title(self):
        title = self.cleaned_data.get('title','')
        if isinstance(title, str):
            title = title.strip()
        return title
    

#? ------------------------------------------------------------------------
#? BaseChoiceFormSet
#? - This is the central place for cross-form validation for Choice inline formsets:
#?     * rejecting emptied initial forms unless marked DELETE,
#?     * enforcing minimum count of choices for multiple-choice questions,
#?     * preventing duplicates,
#?     * optionally transforming/normalizing cleaned_data before save.
#? ------------------------------------------------------------------------
class BaseChoiceFormset(BaseInlineFormSet):

    def clean(self):
        """
        #? Called after each individual form's clean() has run.
        #? Steps performed here:
        #? 1. Call super().clean() to let built-in checks (management form etc.) run.
        #? 2. Iterate over forms and:
        #?     - Safely read cleaned_data
        #?     - Respect the DELETE flag
        #?     - If an initial (existing) form is emptied but not flagged for delete ->
        #?         add a field error (form.add_error('title', '...'))
        #? 3. Count how many non-deleted, non-empty titles remain.
        #? 4. Determine whether the *parent question* (self.instance) is multiple_choice.
        #?     - If instance exists and has question_type, use that.
        #?     - Otherwise, fallback to reading the posted `question_type` from self.data.
        #?       (This is necessary in create flow: parent may be unsaved but the question form
        #?        posts 'question_type' alongside the choice formset because hx-include="closest form".)
        #? 5. If parent is multiple_choice and the count < MIN_CHOICES: raise ValidationError
        #? 6. Also detect duplicates (case-insensitive) and add field errors where duplicates occur.
        #*
        #* Important: raise ValidationError() for formset-level errors (shows via non_form_errors).
        #*            Use form.add_error() to attach field-level errors so they appear near inputs.
        """
        super().clean()

        total_choices = 0
        titles_seen = {}
        empty_intials = []

        for form in self.forms:
            cleaned = getattr(form, 'cleaned_data', None)
            if not cleaned:
                #* There are individual form errors; those will be shown to user.
                #* We still continue to other forms to gather counts/duplicates based on valid forms.
                continue

            delete_flag = cleaned.get('DELETE', False)
            title = cleaned.get('title', '') or ''
            clean_title = title.strip().lower() if isinstance(title, str) else str(title).strip().lower()

            #* When the choice was an initial choice and was existing in the DB, and now it has no value and title is empty:
            if form.initial and not delete_flag and not clean_title:
                #* the formset itself will add a form error for this form. we add it to empty_initials list.
                empty_intials.append(form)

            if clean_title and not delete_flag:
                total_choices += 1
                if clean_title in titles_seen:
                    form.add_error('title', 'Duplicate Choice')
                    try:
                        first_form = titles_seen[clean_title]
                        first_form.add_error('title', 'Duplicate Choice')
                    except:
                        pass
                else:
                    titles_seen[clean_title] = form

        skip_min = getattr(self, 'skip_min', False)
        if not skip_min:
            if total_choices < 2:
                raise ValidationError('A multiple-choice question must have at least 2 choices')
            
        if empty_intials:
            #* then there is form errors on the forms, so we add a help message above them to tell them why
            raise ValidationError('Existing choice cannot be blank. Either fill it or check Delete.')






    
    
#? choice formsets for update and create, only difference being extra forms.
#? their formset is BaseChoiceFormset to help them validate and clean as i want.
ChoiceFormSetCreate = inlineformset_factory(
    Question,
    Choice, 
    form=ChoiceForm,
    formset=BaseChoiceFormset,
    can_delete=True, 
    can_order=False, 
    extra=2)

ChoiceFormSetUpdate = inlineformset_factory(
    Question,
    Choice, 
    form=ChoiceForm,
    formset=BaseChoiceFormset,
    can_delete=True, 
    can_order=False, 
    extra=0)