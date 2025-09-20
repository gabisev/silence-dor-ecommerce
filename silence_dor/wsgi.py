"""
WSGI config for silence_dor project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# Configuration pour la production
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'silence_dor.settings_production')

application = get_wsgi_application()