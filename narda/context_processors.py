from django.contrib.sites.models import Site


def add_domain(request):
    return {
        'DOMAIN': Site.objects.get_current().domain
    }
