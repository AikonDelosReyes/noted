from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from PIL import Image
import os

def validate_image_size(value):
    if value.size > 2 * 1024 * 1024:  # 2MB
        raise ValidationError('Image size must be less than 2MB.')

def validate_image_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    if ext not in valid_extensions:
        raise ValidationError('Unsupported file extension. Please use JPEG, PNG, or WebP.')

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    photo = models.ImageField(
        upload_to='profile_photos/',
        validators=[validate_image_size, validate_image_extension],
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.photo:
            img = Image.open(self.photo.path)
            # Convert to square format
            if img.height != img.width:
                side_length = min(img.height, img.width)
                left = (img.width - side_length) // 2
                top = (img.height - side_length) // 2
                right = left + side_length
                bottom = top + side_length
                img = img.crop((left, top, right, bottom))
                img.save(self.photo.path)

    def __str__(self):
        return f"{self.user.username}'s profile"

class Notebook(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notebooks')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tags')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

class Note(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    notebook = models.ForeignKey(Notebook, on_delete=models.CASCADE, related_name='notes')
    tags = models.ManyToManyField(Tag, related_name='notes', blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
