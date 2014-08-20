from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.template import RequestContext, loader

from frontend.models import Meal

def index(request):
    context = RequestContext(request, {'request': request, 'user': request.user})
    return render_to_response('index.html', context_instance=context)

def search(request, date):
    meal_list = Meal.objects.order_by('-scheduled_for').select_related('kitchen')#[:5]
    context = RequestContext(request, {
        'request': request,
        'user': request.user,
        'meal_list': meal_list,
        'date': date
    })
    return render_to_response('index.html', context_instance=context)

def kitchen_detail(request, date, kitchen_slug):
    return HttpResponse("You're looking at kitchen %s for date %s." % (kitchen_slug , date))
