from django.urls import path
from .views import (
    survey_creation_view, 
    survey_edit_view, 
    survey_detail_view, 
    survey_delete_view, 
    question_create_view,
    question_delete_view,
    question_view,
    choice_create_view
)


app_name = 'survey'
urlpatterns = [
    path("<slug:slug>/detail/", survey_detail_view , name="detail"),

    path("create/title/", survey_creation_view, name="create-title"),
    path("<slug:slug>/edit/", survey_edit_view, name="edit"),
    path("<slug:slug>/delete/", survey_delete_view, name="delete"),

    path("<slug:parent_slug>/question/<int:id>/update/", question_create_view ,name="question-update"),
    path("<slug:parent_slug>/question/create/", question_create_view ,name="question-create"),
    path("<slug:parent_slug>/question/<int:id>/delete/", question_delete_view ,name="question-delete"),
    path("<slug:parent_slug>/question/<int:id>/", question_view ,name="question-detail"),

    # these are not being used anymore, but i'll let them be for now
    path("question/<int:q_id>/choice/<int:c_id>/update/", choice_create_view, name="choice-update"),
    path("question/<int:q_id>/choice/create/", choice_create_view, name="choice-create"),
    #path("<slug:parent_slug>/question/<int:q_id>/choice/<int:c-id>/delete/",,name="choice-delete"),

   
]