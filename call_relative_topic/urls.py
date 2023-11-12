from django.urls import path
from .views import get_go_trends, get_dl_trends

urlpatterns =[
    path('get-go-trends/', get_go_trends),
    path('get-dl-trends/', get_dl_trends),
]