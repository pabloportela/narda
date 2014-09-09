from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string
from django.utils import timezone

from frontend.models import Meal, KitchenReview
from notification.models import Notification


class Command(BaseCommand):
    help = """
        Create review objects and send invitation emails for each meal that
        has happened but no review has been created.
        """

    def handle(self, *args, **kwargs):
        now = timezone.now()
        meal_list = Meal.objects.filter(
            scheduled_for__lt=now,
            review__isnull=True,
            status='a',
        )
        for meal in meal_list:
            print "Creating a KitchenReview object and sending email " \
                "for meal with ID: %d" % meal.id
            token = get_random_string()
            kitchen_review = KitchenReview.objects.create(
                token=token,
                guest=meal.guest,
                kitchen=meal.kitchen,
            )
            meal.review = kitchen_review
            meal.save()
            Notification.notify(
                'invite_guest_review', {
                    'to_address': meal.guest.email,
                    'meal': meal,
                    'kitchen_review': kitchen_review,
                }
            )
