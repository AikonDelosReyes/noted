from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from .serializers import (
    RegisterSerializer, 
    NotebookSerializer,
    NoteSerializer,
    TagSerializer
)
from .models import Notebook, Note, Tag
from .decorators import rate_limit

class CustomUserRateThrottle(UserRateThrottle):
    rate = '20/minute'

class CustomAnonRateThrottle(AnonRateThrottle):
    rate = '5/minute'

class RegisterView(APIView):
    throttle_classes = [CustomAnonRateThrottle]
    
    @rate_limit(requests=3, interval=60)
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User registered successfully!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [CustomUserRateThrottle]

    @rate_limit(requests=10, interval=60)
    def get(self, request):
        return Response({'message': f'Hello, {request.user.username}! You are authenticated.'})

class NotebookViewSet(viewsets.ModelViewSet):
    serializer_class = NotebookSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [CustomUserRateThrottle]

    def get_queryset(self):
        return Notebook.objects.filter(owner=self.request.user)

class NoteViewSet(viewsets.ModelViewSet):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [CustomUserRateThrottle]

    def get_queryset(self):
        return Note.objects.filter(owner=self.request.user)

class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [CustomUserRateThrottle]

    def get_queryset(self):
        return Tag.objects.filter(created_by=self.request.user)

# Create your views here.
