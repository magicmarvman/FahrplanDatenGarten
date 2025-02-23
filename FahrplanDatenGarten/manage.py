#!/usr/bin/env python3
"""Django's command-line utility for administrative tasks."""
import os
import sys
import dotenv
from pathlib import Path

def main():
    dotenv.read_dotenv(os.path.join(os.path.dirname(__file__), os.pardir, '.env'), override=True)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FahrplanDatenGarten.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
