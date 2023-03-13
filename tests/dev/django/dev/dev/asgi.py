"""
ASGI config for dev project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os
import sys

from django.core.asgi import get_asgi_application

from tests.settings import ROOT_DIR

sys.path.append(os.path.join(ROOT_DIR, "dev", "django", "dev"))  # for dev.settings
sys.path.append(os.path.join(ROOT_DIR, "dev"))  # for djangoorm


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dev.settings")

application = get_asgi_application()
