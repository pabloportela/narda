from django.contrib.sites.models import Site


FROM_ADDRESS = 'canalcook.com <info@' + Site.objects.get_current().domain + '>'
