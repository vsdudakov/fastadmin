import os
import sys

from tests.settings import ROOT_DIR

sys.path.append(os.path.join(ROOT_DIR, "environment", "django", "dev"))  # for dev.settings
sys.path.append(os.path.join(ROOT_DIR, "environment"))  # for djangoorm
