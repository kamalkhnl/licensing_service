from django.urls import path
from . import views

urlpatterns = [
    path('assign_key/', views.assign_key, name='assign_key'),
    path('check_key/', views.check_key, name='check_key'),
]