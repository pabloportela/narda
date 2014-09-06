from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta

from frontend.models import Meal, KitchenReview
from frontend.forms import KitchenReviewForm


def index(request):
    context = RequestContext(
        request,
        {'request': request, 'user': request.user}
    )
    return render_to_response('index.html', context_instance=context)


def search(request, date, number_of_guests):
    arg_datetime = datetime.strptime(date, '%Y-%m-%d')
    one_day = timedelta(1)
    meal_list = Meal.objects.filter(
        scheduled_for__lt=(arg_datetime + one_day),
        scheduled_for__gt=arg_datetime,
        status__exact='o',
        kitchen__available_seats__gte=int(number_of_guests)
    ).order_by(
        'scheduled_for'
    ).select_related('kitchen')
    context = RequestContext(request, {
        'request': request,
        'user': request.user,
        'meal_list': meal_list,
        'date': date, 
        'number_of_guests': number_of_guests
    })
    return render_to_response('index.html', context_instance=context)


def kitchen_detail(request, date, hour, minute, kitchen_slug):
    meal = Meal.objects.select_related('kitchen').get(
        kitchen__slug=kitchen_slug,
        scheduled_for=date + " " + hour + ":" + minute
    )
    if not meal:
        raise Http404()

    context = RequestContext(request, {
        'request': request,
        'user': request.user,
        'meal': meal,
        'available_seats': range(1, meal.kitchen.available_seats + 1),
        'image_number': range(1, 6)
    })
    return render_to_response(
        'kitchen/kitchen_detail.html', context_instance=context)


@login_required
def book(request):
    meal_id = request.POST.get('meal_id')
    meal = get_object_or_404(Meal, id=meal_id)
    meal.book(request.user)

    context = RequestContext(request, {
        'request': request,
        'user': request.user,
        'meal': meal,
    })
    return render_to_response(
        'meal/booking_details.html', context_instance=context)


def site_info(request, content):
    context = RequestContext(
        request, {'request': request, 'content': content})
    return render_to_response(
        'site_info/' + content + '.html', context_instance=context)


@login_required
def my_meals(request):
    dine_meals = {}
    for meal_type, status in { 'upcoming':'a', 'done':'d'}.iteritems():
        dine_meals[meal_type] = Meal.objects.filter(
            guest=request.user,
            status=status,
        ).order_by(
            'scheduled_for'
        ).select_related("kitchen")

    cook_meals = {}
    for meal_type, status in { 'open':'o', 'upcoming':'a', 'done':'d', 'cancelled':'c' }.iteritems():
        cook_meals[meal_type] = Meal.objects.filter(
            kitchen__chef=request.user,
            status=status,
        ).order_by(
            'scheduled_for'
        ).select_related("kitchen")

    context = RequestContext(request, {
        'request': request,
        'has_meals' : any(dine_meals.values()) or any(cook_meals.values()),

        'dine_meal_list_upcoming' : dine_meals['upcoming' ],
        'dine_meal_list_done'     : dine_meals['done'     ],

        'cook_meal_list_upcoming' : cook_meals['upcoming' ],
        'cook_meal_list_open'     : cook_meals['open'     ],
        'cook_meal_list_cancelled': cook_meals['cancelled'],
        'cook_meal_list_done'     : cook_meals['done'     ],
    })
    return render_to_response(
        'dashboard/my_meals.html', context_instance=context)


def post_guest_review(request, kitchen_slug, token):
    review_list = KitchenReview.objects.filter(
        token=token,
        reviewed_at__isnull=True
    ).select_related(
        'kitchen',
        'meal'
    )
    if not review_list:
        raise Http404()
    review = review_list[0]

    if request.method == 'GET':
        form = KitchenReviewForm()
    else:
        form = KitchenReviewForm(
            request.POST, instance=review)
        if form.is_valid():
            form.save()

    context = RequestContext(request, {
        'review': review,
        'kitchen': review.kitchen,
        'meal': review.meal,
        'form': form,
    })
    return render_to_response(
        'review/guest_review.html',
        context_instance=context
    )
