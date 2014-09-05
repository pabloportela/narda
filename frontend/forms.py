from django.forms import ModelForm

from frontend.models import KitchenReview


class KitchenReviewForm(ModelForm):
    class Meta:
        model = KitchenReview
        fields = ['rating', 'review']
