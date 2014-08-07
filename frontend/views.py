from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader

from frontend.models import Meal

def index(request):
    return render(request, 'index.html')

def search(request, date):
    meal_list = Meal.objects.order_by('-scheduled_for')#[:5]
    context = {'meal_list': meal_list, 'date': date}
    return render(request, 'search.html', context)

def chef_detail(request, chef_id):
    return HttpResponse("You're looking at chef %s." % chef_id)

