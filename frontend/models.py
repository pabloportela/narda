from django.db import IntegrityError, DatabaseError, transaction, models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.utils import timezone
from autoslug import AutoSlugField
from django.conf import settings
from frontend.exceptions import UserException
import stripe
import json

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
    enabled = models.BooleanField()
    
    def __unicode__(self):
        return "%s (%s)" % (self.name, self.chef.username)

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
    number = models.CharField(max_length=6, db_index=True, null=True, blank=True)
    created_at = models.DateTimeField('date created', auto_now=True)
    accepted_at = models.DateTimeField(blank=True, null=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)
    # Open, Payment pending, Accepted, Done, Noshow, Canceled, Expired
    # Canceled: Chef canceled the meal. If the guest cancels it will go back to
    # Open.
    status = models.CharField(max_length=1, default='o')
    number_of_guests = models.IntegerField(blank=True,null=True)
    review = models.OneToOneField(KitchenReview,blank=True,null=True)

    def __unicode__(self):
        return "%s for %s , %s" % (self.kitchen, self.scheduled_for.strftime("%c"), self.status)

    def meal_datetime(self):
        # We need to transform to naive datetime to show to users.
        scheduled_for = timezone.make_naive(
            self.scheduled_for,
            timezone.get_default_timezone()
        )
        return str(scheduled_for.date()) + "/%02d/%02d" % (
            scheduled_for.hour, scheduled_for.minute)

    def hour_formatted(self):
        return "%02d" % (self.scheduled_for.hour)

    def minute_formatted(self):
        return "%02d" % (self.scheduled_for.minute)

    def description(self):
        return 'This is the meal description'

    @staticmethod
    def _get_meal_to_book(meal_id,number_of_guests):
        with transaction.atomic():
            # get the meal with row lock
            try:
                meal = Meal.objects.select_for_update().get(id=meal_id)
            except Meal.DoesNotExist:
                raise Exception("Meal does not exist")

            # validation
            if meal.status != 'o': # not 'o'open to book
                raise Exception('The meal is not available anymore')

            if int(number_of_guests) > int(meal.kitchen.available_seats):
                raise Exception('The available kitchen seats are not enough for your meal request')

            # put a hold on the meal till we charge
            meal.status = 'p' # 'p'ending payment
            # end of the transaction
            meal.save()

            return meal

    def _do_book(self,number_of_guests,user):
        # booking core
        self.status = 'a' # 'a'ccepted
        self.number_of_guests = number_of_guests
        self.guest = user
        self.accepted_at = timezone.now()
        self.number = self.generate_meal_number()
        self.save()

    @staticmethod
    def book(meal_id,user,number_of_guests,stripe_token):
        # lock the meal so nobody gets in the way
        meal = Meal._get_meal_to_book(meal_id,number_of_guests)
        # charge via stripe token
        try:
            meal.stripe_charge(stripe_token)
        except Exception as e:
            # payment failed, we leave the meal as it was (an update is atomic)
            meal.status = 'o' # 'o'pen to book
            meal.save()
            raise e
        # do the actual booking
        meal._do_book(number_of_guests,user)
        # set up notifications (mail for now)
        meal.notify()

        return meal


    def notify(self):
        # Guest confirmation
        Notification.notify('book_guest', {
            'to_address': self.guest.email,
            'meal': self,
        })
        # Chef confirmation
        Notification.notify('book_chef', {
            'to_address': self.kitchen.chef.email,
            'meal': self,
        })

    def generate_meal_number(self):
        return get_random_string(length=6, allowed_chars='1234567890')

    def stripe_charge(self,token):
        try:
            stripe.api_key = settings.STRIPE_SECRET
            charge = stripe.Charge.create(
                amount=300,
                currency="eur",
                card=token,
                description="Meal id "+str(self.id)
            )

        # declined -> log, let user know the details
        except stripe.error.CardError as e:
            #import ipdb; ipdb.set_trace();
            self._log_failed_mop_payment(e,token,True)
            raise UserException(e)

        # other errors with Stripe
        except (
            stripe.error.AuthenticationError,
            stripe.error.InvalidRequestError,
            stripe.error.APIConnectionError,
            stripe.error.StripeError
            ) as e:
            # log all the details
            self._log_failed_mop_payment(e,token,False)
            # show generic error message
            raise UserException("There was an error in the payment process")

        # other errors, log all details, show generic error
        except Exception as e:
            self._log_failed_mop_payment(e,token,True)
            raise UserException("There was an error in the payment process")

        #success, we log
        try:
            self._log_successful_mop_payment(token,charge)
        # we could not log the payment, but we want to move forward 
        # and let the user know the payment went fine
        except Exception:
            pass

    # mop means method of payment
    def _log_failed_mop_payment(self,message,token,communication_successful):
        transaction = Transaction(
            communication_successful = communication_successful,
            payment_successful = False,
            meal = self,
            gateway = 's',
            token = token,
            json_result = message
        )
        transaction.save()

    def  _log_successful_mop_payment(self,token,charge):
        transaction = Transaction(
            communication_successful = True,
            payment_successful = charge.paid,
            meal = self,
            amount = charge.amount,
            currency = charge.currency,
            gateway = 's',
            token = token,
            json_result = json.dumps(charge)
        )
        transaction.save()


#TODO(pablo) subclass this thing with StripeTransaction to abstract ourselves from that MOP
class Transaction(models.Model):
    meal = models.ForeignKey(Meal)
    created_at = models.DateTimeField(auto_now_add=True)
    communication_successful = models.BooleanField()
    payment_successful = models.BooleanField()
    amount = models.IntegerField(blank=True, null=True)
    currency = models.CharField(max_length=3,blank=True, null=True)
    # Stripe
    gateway = models.CharField(max_length=1, default='s')
    token = models.CharField(max_length=40)
    json_result = models.TextField()


class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    biography = models.TextField()


class Invoice(models.Model):
    invoiced = models.ForeignKey(User)
    amount = models.FloatField()
    due_at = models.DateTimeField('due at')
    payed_at = models.DateTimeField(null=True)
