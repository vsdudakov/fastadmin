import os
import sys

import django

from tests.settings import ROOT_DIR

os.environ["ADMIN_USER_MODEL"] = "User"
os.environ["ADMIN_USER_MODEL_USERNAME_FIELD"] = "username"
os.environ["ADMIN_SECRET_KEY"] = "secret"


sys.path.append(str(ROOT_DIR / "environment" / "django"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dev.settings")
django.setup(set_prefix=False)
