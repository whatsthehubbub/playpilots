#!/usr/bin/env python

import sys

sys.path.append('/Users/alper/Documents/projects/play/site/Django-1.2.1')
sys.path.append('/Users/alper/Documents/projects/play/site/')

# Because it won't catch PIL otherwise, fucking bugger!
sys.path.append('/Library/Python/2.6/site-packages/')

# sys.path.append('/home/alper/shohaiti/Django-1.1.1/')
# sys.path.append('/home/alper/shohaiti/')


from django.core.management import execute_manager
try:
    import settings # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

if __name__ == "__main__":
    execute_manager(settings)
