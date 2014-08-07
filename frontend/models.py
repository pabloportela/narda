from django.db import models
from django.contrib.auth.models import User



class Availability(models.Model):
    chef = models.ForeignKey(User)
    created_at = models.DateTimeField('date created')
    available_at = models.DateTimeField('date of availability')
    available_seats = models.IntegerField()
    suggested_price = models.IntegerField()
    is_available = models.IntegerField(default=1)

    def __unicode__(self):
        return self.available_at


class Inquiry(models.Model):
    availability = models.ForeignKey(Availability)
    guest = models.ForeignKey(User)
    result = models.CharField(max_length=1) # accepted, rejected


class InquiryText(models.Model):
    inquiry = models.ForeignKey(Inquiry)
    source = models.CharField(max_length=1) # guest, chef
    text = models.CharField(max_length=255)
    created_at = models.DateTimeField('date created')
    type = models.CharField(max_length=1) # accept, reject, inquiry


class Meal(models.Model):
    created_at = models.DateTimeField('date created')
    held_at = models.DateTimeField('date created')
    chef = models.ForeignKey(User, related_name="chef")
    guest = models.ForeignKey(User, related_name="guest")
    cancelled_at = models.DateTimeField('date cancelled')

    
class Review(models.Model):
    created_at = models.DateTimeField('date created')
    guest = models.ForeignKey(User)
    meal = models.ForeignKey(Meal)
    text = models.CharField(max_length=255)


class Menu(models.Model):
    chef = models.ForeignKey(User)
    text = models.CharField(max_length=255)


