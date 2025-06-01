from celery import shared_task
from django.core.mail import send_mail
from PIL import Image
import os
from django.utils import timezone
from datetime import timedelta
from .models import User, Note, Notebook, Tag
from .external_apis import WeatherAPI
import json
from django.conf import settings
from django.db import models

@shared_task
def process_profile_photo(photo_path):
    """Process uploaded profile photos in the background."""
    if os.path.exists(photo_path):
        img = Image.open(photo_path)
        if img.height > 500 or img.width > 500:
            output_size = (500, 500)
            img.thumbnail(output_size)
            img.save(photo_path)
    return True

@shared_task
def send_welcome_email(user_email):
    """Send welcome email to new users."""
    subject = 'Welcome to Noted!'
    message = 'Thank you for joining Noted! Start creating your notebooks and notes today.'
    from_email = 'noreply@noted.com'
    recipient_list = [user_email]
    
    send_mail(subject, message, from_email, recipient_list)
    return True

@shared_task
def generate_user_stats(user_id):
    """Generate user statistics in the background."""
    from .models import User, Note, Notebook, Tag
    
    user = User.objects.get(id=user_id)
    stats = {
        'total_notes': Note.objects.filter(owner=user).count(),
        'total_notebooks': Notebook.objects.filter(owner=user).count(),
        'total_tags': Tag.objects.filter(created_by=user).count(),
        'last_active': user.last_login.isoformat() if user.last_login else None
    }
    return stats

@shared_task
def update_notes_weather():
    """
    Periodic task to update weather information for all notes with weather data.
    Runs every 3 hours.
    """
    notes = Note.objects.exclude(weather_city__isnull=True).exclude(weather_city='')
    for note in notes:
        weather_data = WeatherAPI.get_weather(note.weather_city)
        if weather_data:
            note.weather_temp = weather_data['main']['temp']
            note.weather_description = weather_data['weather'][0]['description']
            note.weather_humidity = weather_data['main']['humidity']
            note.save()

@shared_task
def backup_notes():
    """
    Daily task to backup all notes to JSON files.
    Creates a new backup file each day.
    """
    backup_dir = os.path.join(settings.BASE_DIR, 'backups', 'notes')
    os.makedirs(backup_dir, exist_ok=True)
    
    # Create backup filename with timestamp
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f'notes_backup_{timestamp}.json')
    
    # Get all notes with related data
    notes = Note.objects.select_related('owner', 'notebook').prefetch_related('tags').all()
    
    # Prepare data for backup
    backup_data = []
    for note in notes:
        note_data = {
            'id': note.id,
            'title': note.title,
            'content': note.content,
            'owner': note.owner.username,
            'notebook': note.notebook.title,
            'tags': [tag.name for tag in note.tags.all()],
            'created_at': note.created_at.isoformat(),
            'updated_at': note.updated_at.isoformat(),
            'weather_data': {
                'city': note.weather_city,
                'temperature': note.weather_temp,
                'description': note.weather_description,
                'humidity': note.weather_humidity
            } if note.weather_city else None
        }
        backup_data.append(note_data)
    
    # Write backup to file
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, indent=2, ensure_ascii=False)
    
    # Remove backups older than 30 days
    cleanup_old_backups(backup_dir)
    
    return f"Backup created: {backup_file}"

@shared_task
def cleanup_old_backups(backup_dir):
    """Remove backup files older than 30 days."""
    cutoff_date = timezone.now() - timedelta(days=30)
    for filename in os.listdir(backup_dir):
        filepath = os.path.join(backup_dir, filename)
        if os.path.getctime(filepath) < cutoff_date.timestamp():
            os.remove(filepath)

@shared_task
def calculate_user_activity_metrics(user_id):
    """
    Calculate various activity metrics for a user.
    """
    user = User.objects.get(id=user_id)
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    
    # Get notes created in last 30 days
    recent_notes = Note.objects.filter(
        owner=user,
        created_at__gte=thirty_days_ago
    )
    
    # Calculate metrics
    metrics = {
        'notes_last_30_days': recent_notes.count(),
        'avg_notes_per_day': recent_notes.count() / 30,
        'most_used_tags': list(
            Tag.objects.filter(notes__owner=user)
            .annotate(usage_count=models.Count('notes'))
            .order_by('-usage_count')
            .values('name', 'usage_count')[:5]
        ),
        'total_content_length': sum(len(note.content) for note in recent_notes),
        'last_active': user.last_login.isoformat() if user.last_login else None
    }
    
    return metrics 