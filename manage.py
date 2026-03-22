#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # -----------------------------
    # Railway-compatible port
    # -----------------------------
    # Use Railway's PORT environment variable, fallback to 8000 locally
    port = os.environ.get("PORT", "8000")

    # If running the dev server, override sys.argv to include the correct port
    if len(sys.argv) == 1 or sys.argv[1] == "runserver":
        # Bind to all interfaces so Railway can route traffic
        sys.argv = [sys.argv[0], "runserver", f"0.0.0.0:{port}"]

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()