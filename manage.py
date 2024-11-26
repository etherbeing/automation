#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import subprocess

def start_celery():
    """Start Celery worker and Beat."""
    print("Starting Celery worker and Beat...")
    celery_worker = subprocess.Popen(['python3', '-m', 'celery', '-A', 'base', 'worker', '--loglevel=info'])
    celery_beat = subprocess.Popen(['python3', '-m', 'celery', '-A', 'base', 'beat', '--loglevel=info'])
    return celery_worker, celery_beat

def stop_celery(celery_worker, celery_beat):
    """Stop Celery processes."""
    print("Stopping Celery worker and Beat...")
    celery_worker.terminate()
    celery_beat.terminate()


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'base.settings')
    # if len(sys.argv) > 1 and sys.argv[1] == 'runserver':
    #     celery_worker, celery_beat = start_celery()
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    # try:
    execute_from_command_line(sys.argv)
    # finally:
    #     # Stop Celery processes only if they were started
    #     if len(sys.argv) > 1 and sys.argv[1] == 'runserver':
    #         stop_celery(celery_worker, celery_beat)

if __name__ == '__main__':
    main()
