import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Create the Celery app
app = Celery('noted')

# Load task modules from all registered Django app configs
app.config_from_object('django.conf:settings', namespace='CELERY')

# Configure the Celery beat schedule
app.conf.beat_schedule = {
    'update-weather-every-3-hours': {
        'task': 'users.tasks.update_notes_weather',
        'schedule': crontab(minute=0, hour='*/3'),  # Run every 3 hours
    },
    'daily-notes-backup': {
        'task': 'users.tasks.backup_notes',
        'schedule': crontab(minute=0, hour=0),  # Run at midnight
    },
    'calculate-user-metrics': {
        'task': 'users.tasks.calculate_user_activity_metrics',
        'schedule': crontab(minute=0, hour='*/12'),  # Run twice daily
    },
}

# Auto-discover tasks in all installed apps
app.autodiscover_tasks() 