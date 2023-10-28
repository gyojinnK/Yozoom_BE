from django.urls import path
from .views import analysis_view

urlpatterns =[
    path('get-predict-data/', analysis_view),
]