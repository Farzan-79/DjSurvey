from .models import UserProfile
from django import forms

class profile_completion_form(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'bio', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = UserProfile.objects.filter(email__iexact=email)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('this E-mail is already in use')
        return email
        
