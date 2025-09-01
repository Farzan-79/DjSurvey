from django import forms
from .models import Survey, Question, Choice, Answer

class SurveyCreationForm(forms.ModelForm):
    class Meta:
        model= Survey
        fields= ['title', 'description'] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['title'].label = 'Title'
        self.fields['title'].widget.attrs.update({
            "placeholder": "Your Survey Name",
            "class": "form-control"
        })

        self.fields['description'].label = "Description"
        self.fields['description'].widget.attrs.update({
            "placeholder": "Extra information about your survey",
            "rows": "3",
            "class": "form-control"
        })