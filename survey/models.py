from django.db import models
from django.conf import settings
from django.urls import reverse
from .utils import slugify_instance_name

# Create your models here.

class Survey(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='survey')
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created = models.DateField(auto_now_add=True)
    slug = models.SlugField(unique= True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.slug is None:
            slugify_instance_name(self)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('survey:detail', kwargs={'slug': self.slug})
    
    def get_edit_url(self):
        return reverse('survey:edit', kwargs={'slug': self.slug})
    
    def get_delete_url(self):
        return reverse('survey:delete', kwargs={'slug': self.slug})




class Question(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    title = models.CharField(max_length=255)
    question_type = models.CharField(max_length=25, choices=[('multiple_choice', 'Multiple Choice'), ('text', 'Text Answer')])

    def get_absolute_url(self):
        return reverse('survey:question-detail', kwargs={'id': self.id, 'parent_slug': self.survey.slug})

    def get_edit_url(self):
        return reverse('survey:question-update', kwargs={'id': self.id, 'parent_slug': self.survey.slug})
    
    def get_delete_url(self):
        return reverse('survey:question-delete', kwargs={'id': self.id, 'parent_slug': self.survey.slug})





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
    


    
