from django.db import models
from django.contrib.auth.models import User


class Meal(models.Model):
    created_at = models.DateTimeField('date created')
    scheduled_for = models.DateTimeField('scheduled for')
    confirmed_at = models.DateTimeField('confirmed at')
    cancelled_at = models.DateTimeField('cancelled at')
    chef = models.ForeignKey(User, related_name='chef')
    guest = models.ForeignKey(User, related_name='guest')
    available_seats = models.IntegerField()
    suggested_price = models.IntegerField()
    is_available = models.IntegerField(default=1)

    def description():
        return 'This is the meal description'


class Inquiry(models.Model):
    meal = models.ForeignKey(Meal)
    guest = models.ForeignKey(User)
    result = models.CharField(max_length=1) # Open, Accepted, Rejected, Expired


class InquiryText(models.Model):
    inquiry = models.ForeignKey(Inquiry)
    inquirer = models.ForeignKey(User, related_name='inquirer')
    inquired = models.ForeignKey(User, related_name='inquired')
    text = models.CharField(max_length=255)
    created_at = models.DateTimeField('date created')
    

class Review(models.Model):
    created_at = models.DateTimeField('date created')
    reviewer = models.ForeignKey(User, related_name='reviewer')
    reviewed = models.ForeignKey(User, related_name='reviewed')
    target_type = models.CharField(max_length=1) # who has been reviewed: Guest, Chef


class Menu(models.Model):
    chef = models.ForeignKey(User)
    text = models.CharField(max_length=255)


class Invoice(models.Model):
    invoiced = models.ForeignKey(User)
    amount = models.FloatField()
    due_at = models.DateTimeField('due at')
    payed_at = models.DateTimeField('payed at')

