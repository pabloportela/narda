from django.db import models
from django.template.loader import get_template
from django.template import Context
from django.core.mail import send_mail

from notification.constants import FROM_ADDRESS


class Notification(models.Model):
    from_address = models.CharField(max_length=255)
    to_address = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    # status is an enumerable of p(ending), s(ent), e(rror)
    status = models.CharField(max_length=1, default='p')

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
        ).strip()  # Otherwise we get header errors.
        body = body_template.render(
            Context(
                {
                    'name': meal.guest.get_full_name(),
                    'date': meal.scheduled_for,
                    'kitchen_name': meal.kitchen.name
                }
            )
        )
        sent = send_mail(subject, body, FROM_ADDRESS, [meal.guest.email])
        status = 's' if sent else 'e'
        Notification.objects.create(
            from_address=FROM_ADDRESS,
            to_address=meal.guest.email,
            subject=subject,
            body=body,
            status=status,
        )
