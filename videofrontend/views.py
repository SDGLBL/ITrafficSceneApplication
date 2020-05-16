from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.views import generic


from django.shortcuts import render,get_object_or_404
from django.urls import reverse
from django.http import Http404, HttpResponse
# Create your views here.


def index(request):
    return  render(request,'video/index.html',None)

