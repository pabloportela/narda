from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from frontend.models import Meal


def index(request):
    context = RequestContext(request,
                             {'request': request, 'user': request.user})
    return render_to_response('index.html', context_instance=context)


def search(request, date):
    meal_list = Meal.objects.order_by(
        '-scheduled_for').select_related('kitchen')
    context = RequestContext(request, {
        'request': request,
        'user': request.user,
        'meal_list': meal_list,
        'date': date
    })
    return render_to_response('index.html', context_instance=context)


def kitchen_detail(request, date, time, kitchen_slug):
    meal = Meal.objects.select_related(
        'kitchen').get(kitchen__slug=kitchen_slug,
                       scheduled_for=date + " " + time)
    if not meal:
        raise Http404
    context = RequestContext(request, {
        'request': request,
        'user': request.user,
        'meal': meal,
    })
    return render_to_response('kitchen_detail.html', context_instance=context)


@login_required
def book(request):
    # TODO(tayfun): assert user logged in, otherwise have that done
    meal_id = request.POST.get('meal_id')
    meal = get_object_or_404(Meal, id=meal_id)
    meal.book(request.user)
    return HttpResponse('booking successful! :)')
