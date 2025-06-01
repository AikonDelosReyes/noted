from rest_framework import serializers
from .models import Notebook, Note, Tag, UserProfile, User
from django.db import transaction

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    photo = serializers.ImageField(required=False)

    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'photo']

    def update(self, instance, validated_data):
        if 'photo' in validated_data:
            instance.photo = validated_data['photo']
            instance.save()
        return instance

class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True, required=True)
    photo = serializers.ImageField(required=False)
    
    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'photo')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({
                'password2': "Password fields didn't match."
            })
        return data

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop('password2')
        photo = validated_data.pop('photo', None)
        
        # Create user first
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        
        # Update profile photo if provided
        if photo:
            user.profile.photo = photo
            user.profile.save()
            
        return user

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ('id', 'username', 'profile')

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'created_at']
        read_only_fields = ['created_by']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class NotebookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notebook
        fields = ['id', 'title', 'description', 'created_at', 'updated_at']
        read_only_fields = ['owner']

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)

class NoteSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    weather_city = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Note
        fields = [
            'id', 'title', 'content', 'notebook', 'tags', 'tag_ids',
            'created_at', 'updated_at', 'weather_city', 'weather_temp',
            'weather_description', 'weather_humidity'
        ]
        read_only_fields = ['owner', 'weather_temp', 'weather_description', 'weather_humidity']

    def create(self, validated_data):
        tag_ids = validated_data.pop('tag_ids', [])
        weather_city = validated_data.pop('weather_city', None)
        validated_data['owner'] = self.context['request'].user
        
        note = super().create(validated_data)
        note.tags.set(Tag.objects.filter(id__in=tag_ids))
        
        # Handle weather data
        if weather_city:
            from .external_apis import WeatherAPI
            weather_data = WeatherAPI.get_weather(weather_city)
            if weather_data:
                note.weather_city = weather_city
                note.weather_temp = weather_data['main']['temp']
                note.weather_description = weather_data['weather'][0]['description']
                note.weather_humidity = weather_data['main']['humidity']
                note.save()
        
        return note

    def update(self, instance, validated_data):
        tag_ids = validated_data.pop('tag_ids', None)
        weather_city = validated_data.pop('weather_city', None)
        
        note = super().update(instance, validated_data)
        if tag_ids is not None:
            note.tags.set(Tag.objects.filter(id__in=tag_ids))
            
        # Update weather data if city is provided
        if weather_city:
            from .external_apis import WeatherAPI
            weather_data = WeatherAPI.get_weather(weather_city)
            if weather_data:
                note.weather_city = weather_city
                note.weather_temp = weather_data['main']['temp']
                note.weather_description = weather_data['weather'][0]['description']
                note.weather_humidity = weather_data['main']['humidity']
                note.save()
        
        return note
