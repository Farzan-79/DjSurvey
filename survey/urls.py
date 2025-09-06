from django.urls import path
from .views import survey_creation_view, survey_edit_view, survey_detail_view, survey_delete_view


app_name = 'survey'
urlpatterns = [
    path("<slug:slug>/detail/", survey_detail_view , name="detail"),
    path("create/title/", survey_creation_view, name="create-title"),
    path("<slug:slug>/edit/", survey_edit_view, name="edit"),
    path("<slug:slug>/delete/", survey_delete_view, name="delete"),
]