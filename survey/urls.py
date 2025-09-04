from django.urls import path
from .views import survey_creation_view, survey_edit_view, survey_detail_view


app_name = 'survey'
urlpatterns = [
    path("detail/<slug:slug>", survey_detail_view , name="detail"),
    path("create/title/", survey_creation_view, name="create-title"),
    path("create/edit/<slug:slug>/", survey_edit_view, name="edit"),
]