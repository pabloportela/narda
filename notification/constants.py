from django.contrib.sites.models import Site


FROM_ADDRESS = 'info@' + Site.objects.get_current().domain
