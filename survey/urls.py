from django.urls import path
from .views import survey_creation_view


app_name = 'survey'
urlpatterns = [
    path("create/title/", survey_creation_view, name="create-title"),
    #path("create/question/"),
]