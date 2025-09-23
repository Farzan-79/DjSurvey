from django.urls import path
from .views import (
    survey_creation_view, 
    survey_edit_view, 
    survey_detail_view, 
    survey_delete_view, 
    question_create_view,
    question_update_view,
    question_delete_view,
    question_view,
    choice_area_view
)


app_name = 'survey'
urlpatterns = [

    #* survey basic CRUD
    #* create-title is just the title form alone, then it goes to edit
    path("<slug:slug>/detail/", survey_detail_view , name="detail"),
    path("create/title/", survey_creation_view, name="create-title"),
    path("<slug:slug>/edit/", survey_edit_view, name="edit"),
    path("<slug:slug>/delete/", survey_delete_view, name="delete"),

    #* Question CRUD (HTMX-friendly endpoints)
    #* note: update view used for editing a specific question (HTMX swaps par-question.html / par-question-form.html)
    path("<slug:parent_slug>/question/<int:id>/update/", question_update_view ,name="question-update"),
    path("<slug:parent_slug>/question/create/", question_create_view ,name="question-create"),
    path("<slug:parent_slug>/question/<int:id>/delete/", question_delete_view ,name="question-delete"),
    path("<slug:parent_slug>/question/<int:id>/", question_view ,name="question-detail"),

    #* HTMX endpoint for rendering choice formset area (add form / show existing choices)
    path("<slug:parent_slug>/question/choices/", choice_area_view, name="choice-area"),
]