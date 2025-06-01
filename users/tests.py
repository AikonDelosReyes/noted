from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User, Notebook, Note, Tag, UserProfile
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, MagicMock
from .tasks import generate_user_stats, update_notes_weather, backup_notes
from django.utils import timezone
from datetime import timedelta
import json
import os

class AuthenticationTests(APITestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('api_register')
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password2': 'testpass123'  # Added this field
        }

    def test_user_registration(self):
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())
        # Verify profile was created
        user = User.objects.get(username='testuser')
        self.assertTrue(hasattr(user, 'profile'))

class NotebookTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_authenticate(user=self.user)
        self.notebook_data = {
            'title': 'Test Notebook',
            'description': 'Test Description'
        }

    def test_create_notebook(self):
        response = self.client.post('/users/api/notebooks/', self.notebook_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Notebook.objects.count(), 1)
        self.assertEqual(Notebook.objects.get().title, 'Test Notebook')

class NoteTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.notebook = Notebook.objects.create(
            title='Test Notebook',
            owner=self.user
        )
        self.client.force_authenticate(user=self.user)
        self.note_data = {
            'title': 'Test Note',
            'content': 'Test Content',
            'notebook': self.notebook.id,
            'weather_city': 'London'
        }

    def test_create_note(self):
        response = self.client.post('/users/api/notes/', self.note_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Note.objects.count(), 1)
        self.assertEqual(Note.objects.get().title, 'Test Note')

    @patch('users.external_apis.WeatherAPI.get_weather')
    def test_create_note_with_weather(self, mock_get_weather):
        # Mock weather API response
        mock_get_weather.return_value = {
            'main': {
                'temp': 20.5,
                'humidity': 65
            },
            'weather': [{'description': 'Clear sky'}]
        }

        response = self.client.post('/users/api/notes/', self.note_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        note = Note.objects.get(title='Test Note')
        self.assertEqual(note.weather_city, 'London')
        self.assertEqual(note.weather_temp, 20.5)
        self.assertEqual(note.weather_description, 'Clear sky')
        self.assertEqual(note.weather_humidity, 65)

    @patch('users.external_apis.WeatherAPI.get_weather')
    def test_update_note_weather(self, mock_get_weather):
        # Create a note first
        note = Note.objects.create(
            title='Weather Note',
            content='Content',
            notebook=self.notebook,
            owner=self.user,
            weather_city='Paris'
        )

        # Mock weather API response for update
        mock_get_weather.return_value = {
            'main': {
                'temp': 25.0,
                'humidity': 70
            },
            'weather': [{'description': 'Sunny'}]
        }

        # Update the note
        response = self.client.patch(
            f'/users/api/notes/{note.id}/',
            {'weather_city': 'Paris'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify weather data was updated
        note.refresh_from_db()
        self.assertEqual(note.weather_temp, 25.0)
        self.assertEqual(note.weather_description, 'Sunny')
        self.assertEqual(note.weather_humidity, 70)

class TagTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_authenticate(user=self.user)
        self.tag_data = {
            'name': 'TestTag'
        }

    def test_create_tag(self):
        response = self.client.post('/users/api/tags/', self.tag_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tag.objects.count(), 1)
        self.assertEqual(Tag.objects.get().name, 'TestTag')

class UserProfileTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_authenticate(user=self.user)

    def test_profile_exists(self):
        """Test that a profile is automatically created for new users."""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, UserProfile)

    def test_update_profile_photo(self):
        """Test updating profile photo."""
        # Create a test image
        image_content = b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
        photo = SimpleUploadedFile(
            'test_photo.gif',
            image_content,
            content_type='image/gif'
        )

        response = self.client.patch('/users/api/profile/', {'photo': photo})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.profile.photo)

class TaskTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.notebook = Notebook.objects.create(
            title='Test Notebook',
            owner=self.user
        )
        self.note = Note.objects.create(
            title='Test Note',
            content='Test Content',
            notebook=self.notebook,
            owner=self.user,
            weather_city='London'
        )

    def test_generate_user_stats(self):
        stats = generate_user_stats(self.user.id)
        self.assertEqual(stats['total_notes'], 1)
        self.assertEqual(stats['total_notebooks'], 1)
        self.assertEqual(stats['total_tags'], 0)

    @patch('users.external_apis.WeatherAPI.get_weather')
    def test_update_notes_weather(self, mock_get_weather):
        mock_get_weather.return_value = {
            'main': {
                'temp': 18.5,
                'humidity': 75
            },
            'weather': [{'description': 'Cloudy'}]
        }

        update_notes_weather()
        
        self.note.refresh_from_db()
        self.assertEqual(self.note.weather_temp, 18.5)
        self.assertEqual(self.note.weather_description, 'Cloudy')
        self.assertEqual(self.note.weather_humidity, 75)

    def test_backup_notes(self):
        # Create a temporary backup directory
        test_backup_dir = 'test_backups'
        os.makedirs(test_backup_dir, exist_ok=True)

        with patch('config.settings.BASE_DIR', test_backup_dir):
            result = backup_notes()
            
            # Verify backup file was created
            self.assertTrue(os.path.exists(result.split(': ')[1]))
            
            # Verify backup content
            with open(result.split(': ')[1], 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
                self.assertEqual(len(backup_data), 1)
                self.assertEqual(backup_data[0]['title'], 'Test Note')

        # Cleanup
        import shutil
        shutil.rmtree(test_backup_dir)
