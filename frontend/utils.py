from datetime import datetime, timedelta
from django.utils import timezone


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
    if not given_date:
        kwargs["scheduled_for__gt"] = now
        return kwargs
    try:
        parsed_datetime = datetime.strptime(given_date, '%Y-%m-%d/%H/%M')
        parsed_datetime = timezone.make_aware(
            parsed_datetime,
            timezone.get_current_timezone(),
        )
        # FIXME: it is better to redirect so that the user notices it is
        # different now
        # if parsed_datetime < now:
        #     parsed_datetime = now
        kwargs['scheduled_for'] = parsed_datetime
        return kwargs
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
    # FIXME: it is better to redirect so that the user notices it is
    # different now
    # if parsed_datetime < now:
    #     parsed_datetime = now
        # kwargs['scheduled_for__gt'] = parsed_datetime
        # return kwargs
    kwargs["scheduled_for__gt"] = parsed_datetime
    kwargs["scheduled_for__lt"] = parsed_datetime + timedelta(1)
