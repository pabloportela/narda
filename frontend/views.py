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


def search(request, date):
    arg_datetime = datetime.strptime(date, '%Y-%m-%d')
    one_day = timedelta(1)
    meal_list = Meal.objects.filter(
        scheduled_for__lt=(arg_datetime + one_day),
        scheduled_for__gt=arg_datetime,
        status__exact='o'
    ).order_by(
        'scheduled_for'
    ).select_related('kitchen')
    context = RequestContext(request, {
        'request': request,
        'user': request.user,
        'meal_list': meal_list,
        'date': date
    })
    return render_to_response('index.html', context_instance=context)


def kitchen_detail(request, date, time, kitchen_slug):
    meal = Meal.objects.select_related('kitchen').get(
        kitchen__slug=kitchen_slug,
        scheduled_for=date + " " + time
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
    upcoming_dine_meal_list = Meal.objects.filter(
        guest=request.user,
        status='a',
    ).order_by(
        'scheduled_for'
    ).select_related("kitchen")

    upcoming_cook_meal_list = Meal.objects.filter(
        kitchen__chef=request.user,
        status='a',
    ).order_by(
        'scheduled_for'
    ).select_related("kitchen")

    context = RequestContext(request, {
        'request': request,
        'upcoming_dine_meal_list': upcoming_dine_meal_list,
        'upcoming_cook_meal_list': upcoming_cook_meal_list,
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
