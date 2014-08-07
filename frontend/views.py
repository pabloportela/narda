from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello, world. You're at Narda.")

def chef_detail(request, chef_id):
    return HttpResponse("You're looking at chef %s." % chef_id)

