from django.contrib.sites.models import Site

def base(request):    
    # This already is cached by Django.
    site = Site.objects.get_current()

    return {
        'SITE_DOMAIN': 'http://' + site.domain,
    }