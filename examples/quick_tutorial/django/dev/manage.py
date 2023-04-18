#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

from tests.settings import ROOT_DIR

sys.path.append(os.path.join(ROOT_DIR, "..", "examples", "quick_tutorial", "django", "dev"))  # for dev.settings
sys.path.append(os.path.join(ROOT_DIR, "..", "examples", "quick_tutorial"))  # for djangoorm

import django
django.setup(set_prefix=False)

def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dev.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
