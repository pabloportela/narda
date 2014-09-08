from django.forms import ModelForm
from django.utils import timezone


from frontend.models import KitchenReview


class KitchenReviewForm(ModelForm):
    class Meta:
        model = KitchenReview
        fields = ['rating', 'review', 'reviewed_at']

    def clean_reviewed_at(self):
        """
        We don't care what the form provides, always use current datetime.
        """
        return timezone.now()
