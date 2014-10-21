import datetime
import random
from datetime import timedelta
from django.utils import timezone


today = datetime.datetime.now()
all_kitchens = Kitchen.objects.all()

for i in range(365):
    single_date = today + timedelta(i)
    single_date = timezone.make_aware(
        single_date,
        timezone.get_current_timezone(),
    )
    for _j in range(5):
        kitchen = random.choice(all_kitchens)
        single_date = single_date.replace(
            hour=(random.choice(range(24))),
            minute=(random.choice(range(0, 60, 5))),
            second=0
        )
        Meal.objects.create(
            scheduled_for=single_date,
            kitchen=kitchen,
        )

