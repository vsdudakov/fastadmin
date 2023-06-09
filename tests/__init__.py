import os
import sys

from django import setup

from tests.settings import ROOT_DIR

# for dev.settings
sys.path.append(str(ROOT_DIR / "environment" / "django" / "dev"))
# for djangoorm
sys.path.append(str(ROOT_DIR / "environment"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dev.settings")

setup()
