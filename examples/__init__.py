import sys
import os
from tests.settings import ROOT_DIR

sys.path.append(os.path.join(ROOT_DIR, "..", "examples", "django", "dev"))  # for dev.settings
sys.path.append(os.path.join(ROOT_DIR, "..", "examples"))  # for djangoorm
