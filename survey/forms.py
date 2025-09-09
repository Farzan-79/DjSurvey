from django import forms
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

class SurveyQuestionForm(forms.ModelForm):
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