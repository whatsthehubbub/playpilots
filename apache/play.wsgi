import os, sys

sys.path.append('/home/alper/site/Django-1.2.1/')
sys.path.append('/home/alper/site/')
sys.path.append('/home/alper/site/ebi/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'ebi.settings'


import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
