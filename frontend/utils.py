from datetime import datetime, timedelta

from django.utils import timezone

from frontend.constants import BOOKING_WINDOW_HOURS


def add_date(kwargs, given_date):
    """
    Parses a date or datetime (as in the URL parameter) and adds it to the
    query search parameters.

    Example given_date:
        2014-01-01
        2014-01-01/13-00
    etc.
    """
    now = timezone.now()
    meal_booking_window_start = now + timedelta(hours=BOOKING_WINDOW_HOURS)
    # A sane default.
    kwargs["scheduled_for__gt"] = meal_booking_window_start
    has_time = False
    if not given_date:
        return kwargs
    try:
        parsed_datetime = datetime.strptime(given_date, '%Y-%m-%d/%H/%M')
        has_time = True
    except ValueError:
        # Let's try the one without time.
        try:
            parsed_datetime = datetime.strptime(given_date, '%Y-%m-%d')
        except ValueError:
            return kwargs

    parsed_datetime = timezone.make_aware(
        parsed_datetime,
        timezone.get_current_timezone(),
    )

    if has_time:
        kwargs['scheduled_for'] = parsed_datetime
    else:
        if parsed_datetime < meal_booking_window_start:
            start_time = meal_booking_window_start
        else:
            start_time = parsed_datetime
        kwargs["scheduled_for__gt"] = start_time
        kwargs["scheduled_for__lt"] = parsed_datetime + timedelta(1)

    return kwargs
