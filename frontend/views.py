from datetime import datetime, timedelta
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import IntegrityError, DatabaseError, transaction
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages

from frontend.models import Meal, KitchenReview, UserException
from frontend.forms import KitchenReviewForm


def index(request):
    highlighted_meals = Meal.get_highlighted_meals()
    context = RequestContext(
        request,
        {'request': request, 'user': request.user, 'highlighted_meals': highlighted_meals}
    )
    return render_to_response('index.html', context_instance=context)


def search(request, date, number_of_guests):
    '''
    TODO(pablo) search filters by GET does not scale. for now we are ok but
    we gotta do POST and validate when database is bigger and we really have
    to search & sort.
    '''
    arg_datetime = timezone.make_aware(
        datetime.strptime(date, '%Y-%m-%d'),
        timezone.get_current_timezone(),
    )
    one_day = timedelta(1)
    meal_list = Meal.objects.filter(
        scheduled_for__lt=(arg_datetime + one_day),
        scheduled_for__gt=arg_datetime,
        status__exact='o',
        kitchen__available_seats__gte=int(number_of_guests),
        kitchen__enabled=True
    ).order_by(
        'scheduled_for'
    ).select_related('kitchen')
    context = RequestContext(request, {
        'request': request,
        'user': request.user,
        'search': True,
        'meal_list': meal_list,
        'date': date,
        'number_of_guests': number_of_guests
    })
    return render_to_response('index.html', context_instance=context)


def kitchen_detail(request, kitchen_slug,
                   meal_datetime=None, number_of_guests=None):
    """

    """
    meal_datetime = datetime.strptime(meal_datetime, '%Y-%m-%d/%H/%M')
    meal_datetime = timezone.make_aware(
        meal_datetime,
        timezone.get_current_timezone(),
    )
    meal = Meal.objects.prefetch_related(
        'kitchen__reviews',
        'kitchen__chef',
        'kitchen__reviews__guest'
    ).get(
        kitchen__slug=kitchen_slug,
        scheduled_for=meal_datetime,
    )
    if not meal:
        raise Http404()

    context = RequestContext(request, {
        'request': request,
        'user': request.user,
        'meal': meal,
        'available_seats': range(1, meal.kitchen.available_seats + 1),
        'image_number': range(1, 6),
        'number_of_guests': number_of_guests,
        'stripe_key': settings.STRIPE_KEY
    })
    return render_to_response(
        'kitchen/kitchen_detail.html', context_instance=context)


@login_required
def book(request):
    '''
    mysql currently does not support nowait=True so in the case of booking
    concurrency, the unlucky second booker with wait in vain, but will receive
    the proper error message and hopefully we won't have overbookings.

    jesus christ, I hope we have bookings at all.

    anyway, it is important to lock, because at the beggining there won't be
    many chefs and we will charge money upon booking.
    '''
    meal_id = request.POST.get('meal_id')
    number_of_guests = request.POST.get('number_of_guests')
    stripe_token = request.POST.get('stripe_token')

    try:
        meal = Meal.book(
            meal_id, request.user, number_of_guests, stripe_token
        )

    except UserException as e:
        context = RequestContext(request, {
            'user': request.user,
            'message': e
        })
        return render_to_response('meal/meal_payment_error.html', context_instance=context);

    except Exception:
        context = RequestContext(request, { 'user': request.user })
        return render_to_response('meal/meal_payment_error.html', context_instance=context);

    # success
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
    # TODO(Tayfun): Commented out reviewed_at criteria for testing.
    review_list = KitchenReview.objects.filter(
        token=token,
        # reviewed_at__isnull=True
    ).select_related(
        'kitchen',
        'meal'
    )
    if not review_list:
        raise Http404()
    review = review_list[0]

    if not review.reviewed_at:
        if request.method == 'GET':
            form = KitchenReviewForm()
        else:
            form = KitchenReviewForm(
                request.POST, instance=review)
            if form.is_valid():
                form.save()
    else:
        form = None

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
