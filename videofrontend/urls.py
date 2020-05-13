from django.urls import path

from . import views

app_name='videofrontend'
urlpatterns=[path('',views.index,name='index')]