from django.db import models
from django.template.loader import get_template
from django.template import Context
from django.core.mail import send_mail


class Notification(models.Model):

    @staticmethod
    def notify(template_name, meal):
        template_name = 'emails/' + template_name
        subject_template = get_template(
            template_name + '_subject.html')
        body_template = get_template(template_name + '_body.html')
        subject = subject_template.render(
            Context(
                {
                    'name': meal.guest.first_name,
                }
            )
        ).strip()
        body = body_template.render(
            Context(
                {
                    'name': meal.guest.get_full_name(),
                    'date': meal.scheduled_for,
                    'kitchen_name': meal.kitchen.name
                }
            )
        )
        send_mail(subject, body, 'info@haveachef.com', [meal.guest.email])
