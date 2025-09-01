from django.contrib import admin
from .models import *
import nested_admin
# Register your models here.

class ChoiceInline(nested_admin.NestedTabularInline):
    model = Choice
    extra = 1

class QuestionInline(nested_admin.NestedStackedInline):
    model = Question
    extra = 0
    inlines = [ChoiceInline]

class SurveyAdmin(nested_admin.NestedModelAdmin):
    list_display = ['title', 'user']
    readonly_fields = ['created']
    inlines = [QuestionInline]

admin.site.register(Survey, SurveyAdmin)
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(Answer)
