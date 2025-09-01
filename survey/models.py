from django.db import models
from django.conf import settings
# Create your models here.

class Survey(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='survey')
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created = models.DateField(auto_now_add=True)

class Question(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    title = models.CharField(max_length=255)
    question_type = models.CharField(max_length=25, choices=[('multiple_choice', 'Multiple Choice'), ('text', 'Text')])

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    title = models.CharField(max_length=255)
    
class Answer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')

    # if it was multi choice:
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, null=True, blank=True)

    # if it was text:
    text_answer = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'Answer for \"{self.question.title}\" by \"{self.user}\" : {[self.choice.title if self.choice else self.text_answer]}'
    


    
