from django.urls import path
from .views import get_relTopic

urlpatterns =[
    path('get-relative-topic/', get_relTopic),
]