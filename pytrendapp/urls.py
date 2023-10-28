from django.urls import path
from .views import get_go_trends

urlpatterns =[
    path('get-go-trends/', get_go_trends),
]