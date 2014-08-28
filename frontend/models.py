from django.db import models
from django.contrib.auth.models import User
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


class Meal(models.Model):
    scheduled_for = models.DateTimeField('scheduled for')
    kitchen = models.ForeignKey(Kitchen)
    guest = models.ForeignKey(
        User, related_name='guest', blank=True, null=True)
    is_available = models.IntegerField(default=1)

    created_at = models.DateTimeField('date created', auto_now=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)
    # Open, Pending, Accepted, Rejected, Expired
    status = models.CharField(max_length=1, default='o')

    def time(self):
        return "%02d:%02d" % (
            self.scheduled_for.hour, self.scheduled_for.minute)

    def description(self):
        return 'This is the meal description'

    def book(self, user):
        self.guest = user
        self.status = 'p'
        self.save()
        #Notification.notify('book', self)


# TODO(tayfun): Photos need to be added to kitchen as a gallery.
# Convention is to have static/kitchen/user_name as a directory where
# kitchen photos would be put manually and referenced by menu textfield.


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


class Review(models.Model):
    created_at = models.DateTimeField('date created')
    reviewer = models.ForeignKey(User, related_name='reviewer')
    reviewed = models.ForeignKey(User, related_name='reviewed')
    rating = models.IntegerField()
    # who has been reviewed: Guest, Chef
    target_type = models.CharField(max_length=1)


class Invoice(models.Model):
    invoiced = models.ForeignKey(User)
    amount = models.FloatField()
    due_at = models.DateTimeField('due at')
    payed_at = models.DateTimeField(null=True)
