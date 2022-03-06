"""
WSGI config for OstrakovO_DBS_py39 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

settings_module = 'OstrakovO_DBS_py39.production' if 'WEBSITE_HOSTNAME' in os.environ else 'OstrakovO_DBS_py39.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

application = get_wsgi_application()
