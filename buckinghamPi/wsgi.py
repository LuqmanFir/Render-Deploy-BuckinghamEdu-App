"""
WSGI config for buckinghamPi project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

settings_module = 'buckinghamPi.deployment_setting' if 'RENDER_EXTERNAL_HOSTNAME' in os.environ else 'buckinghamPi.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'buckinghamPi.settings')

application = get_wsgi_application()
