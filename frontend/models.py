from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.core import exceptions
from django.utils import timezone

from autoslug import AutoSlugField

from notification.models import Notification


class Kitchen(models.Model):
    chef = models.ForeignKey(User)
    name = models.CharField(max_length=255)
    summary = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    menu = models.TextField()
    dishes_from = models.IntegerField()
    house_rules = models.TextField()
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    slug = AutoSlugField(populate_from='name')
    available_seats = models.IntegerField()


class KitchenReview(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(default=None, null=True, blank=True)
    guest = models.ForeignKey(User, related_name='reviews')
    kitchen = models.ForeignKey(Kitchen, related_name='reviews')
    rating = models.IntegerField(null=True)
    review = models.TextField(null=True)
    token = models.CharField(
        max_length=255, db_index=True
    )


class Meal(models.Model):
    scheduled_for = models.DateTimeField('scheduled for')
    kitchen = models.ForeignKey(Kitchen)
    guest = models.ForeignKey(
        User, related_name='guest', blank=True, null=True)
    is_available = models.IntegerField(default=1)

    created_at = models.DateTimeField('date created', auto_now=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)
    # Open, Accepted, Done, Noshow, Canceled
    # Canceled: Chef canceled the meal. If the guest cancels it will go back to Open.
    # TODO(pablo) isn't "Open" a suitable state for a kitchen rather than a meal?
    # maybe we could use Available here, but already collides with Accepted.
    # how about "Avialable" and "Confirmed" respectively? that also goes with the datetime fields
    status = models.CharField(max_length=1, default='o')
    number_of_guests = models.IntegerField()
    review = models.ForeignKey(KitchenReview, null=True)

    def hour_formatted(self):
        return "%02d" % (self.scheduled_for.hour)

    def minute_formatted(self):
        return "%02d" % (self.scheduled_for.minute)

    def description(self):
        return 'This is the meal description'

# TODO(pablo) we probably need out custom exception class, but this is ok for now
    def book(self, user, number_of_guests):
        # validation
        if self.status != 'o':
            raise Exception('The meal is not available anymore')

        if int(number_of_guests) > int(self.kitchen.available_seats):
            raise Exception('The available kitchen seats are not enough for your meal request')

        # booking core
        self.number_of_guests = number_of_guests
        self.guest = user
        self.confirmed_at = timezone.now()
        self.status = 'a'
        # end of the transaction
        self.save()
        meal_nr = self._generate_meal_number()
        # Guest confirmation
        Notification.notify('book_guest', {
            'to_address': self.guest.email,
            'meal': self,
            'meal_nr': meal_nr,
        })
        # Chef confirmation
        Notification.notify('book_chef', {
            'to_address': self.kitchen.chef.email,
            'meal': self,
            'meal_nr': meal_nr,
        })

    def _generate_meal_number(self):
        length = 9
        for len_try in range(3):
            for rand_try in range (30):
                meal_nr = get_random_string(length=length, allowed_chars='123456789')
                obj, created = MealId_MealNr.objects.get_or_create(meal_nr = meal_nr, meal = self)
                if created:
                    return meal_nr
            length = length + 1
        raise Exception('Gave up trying to generate unique meal_nr')

# TODO(tayfun): Photos need to be added to kitchen as a gallery.
# Convention is to have static/pictures/kitchen/id as a directory where
# kitchen photos would be put manually and referenced by menu textfield.

class MealId_MealNr(models.Model):
    meal_nr = models.IntegerField(primary_key=True)
    meal = models.ForeignKey(Meal, db_index=True)

class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    biography = models.TextField()


class Inquiry(models.Model):
    meal = models.ForeignKey(Meal)
    sender = models.ForeignKey(User, related_name='sent_inquiries')
    receiver = models.ForeignKey(User, related_name='received_inquiries')
    text = models.CharField(max_length=255)
    created_at = models.DateTimeField('date created')
    read_at = models.DateTimeField('receiver read it')
    committed = models.BooleanField()


class Invoice(models.Model):
    invoiced = models.ForeignKey(User)
    amount = models.FloatField()
    due_at = models.DateTimeField('due at')
    payed_at = models.DateTimeField(null=True)
