from django import forms
from django.forms import inlineformset_factory
from .models import Survey, Question, Choice, Answer


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

        #self.fields['title'].label = 'Title'
        #self.fields['title'].widget.attrs.update({
        #    "placeholder": "Your Survey Name",
        #    "class": "form-control"
        #})

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
        super().__init__(*args, **kwargs)
        self.fields['title'].label= 'Question Title'
        self.fields['title'].widget.attrs.update({
            "placeholder": "e.g. What\'s your favorite color?",
            "class": "form-control"
        })

        self.fields['question_type'].label = "Question Type"
        self.fields['question_type'].widget.attrs.update({
            "class": "form-control"
        })


class ChoiceForm(forms.ModelForm):
    class Meta:
        model= Choice
        fields = ['title']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label= 'Choice'
        self.fields['title'].widget.attrs.update({
            'placeholder': "e.g. Choice \'A\'",
            "class": "form-control"
            
        })

ChoiceFormSet = inlineformset_factory(Question, Choice, ChoiceForm, can_delete=True, can_order=False, extra=1)