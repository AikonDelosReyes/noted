from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Notebook, Note, Tag, UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['photo']

class RegisterSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(required=False)
    
    class Meta:
        model = User
        fields = ('username', 'password', 'photo')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        photo = validated_data.pop('photo', None)
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        
        # Create user profile with photo if provided
        profile = UserProfile.objects.create(user=user)
        if photo:
            profile.photo = photo
            profile.save()
            
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

    class Meta:
        model = Note
        fields = ['id', 'title', 'content', 'notebook', 'tags', 'tag_ids', 'created_at', 'updated_at']
        read_only_fields = ['owner']

    def create(self, validated_data):
        tag_ids = validated_data.pop('tag_ids', [])
        validated_data['owner'] = self.context['request'].user
        note = super().create(validated_data)
        note.tags.set(Tag.objects.filter(id__in=tag_ids))
        return note

    def update(self, instance, validated_data):
        tag_ids = validated_data.pop('tag_ids', None)
        note = super().update(instance, validated_data)
        if tag_ids is not None:
            note.tags.set(Tag.objects.filter(id__in=tag_ids))
        return note
