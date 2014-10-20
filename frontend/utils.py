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
    if not given_date:
        return kwargs
    try:
        parsed_datetime = datetime.strptime(given_date, '%Y-%m-%d/%H/%M')
        parsed_datetime = timezone.make_aware(
            parsed_datetime,
            timezone.get_current_timezone(),
        )
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
    kwargs["scheduled_for__gt"] = parsed_datetime
    kwargs["scheduled_for__lt"] = parsed_datetime + timedelta(1)
