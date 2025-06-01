from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .serializers import (
    RegisterSerializer, 
    NotebookSerializer,
    NoteSerializer,
    TagSerializer,
    UserSerializer,
    UserProfileSerializer
)
from .models import Notebook, Note, Tag, UserProfile
from .decorators import rate_limit

class CustomUserRateThrottle(UserRateThrottle):
    rate = '20/minute'

class CustomAnonRateThrottle(AnonRateThrottle):
    rate = '5/minute'

@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.method == "POST":
        data = request.POST.dict()
        if 'photo' in request.FILES:
            data['photo'] = request.FILES['photo']
        
        serializer = RegisterSerializer(data=data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                login(request, user)
                return redirect('home')
            except Exception as e:
                return render(request, 'users/register.html', {'error_message': str(e)})
        return render(request, 'users/register.html', {'error_message': serializer.errors})
    return render(request, 'users/register.html')

@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        return render(request, 'users/login.html', {'error_message': 'Invalid credentials'})
    
    return render(request, 'users/login.html')

@login_required
def home_view(request):
    """View for displaying the home page."""
    notebooks = Notebook.objects.filter(owner=request.user)
    notes = Note.objects.filter(owner=request.user)
    tags = Tag.objects.filter(created_by=request.user)
    
    context = {
        'notebooks': notebooks,
        'notes': notes.order_by('-updated_at'),
        'tags': tags
    }
    return render(request, 'users/home.html', context)

@login_required
def notebook_detail_view(request, notebook_id):
    notebook = get_object_or_404(Notebook, id=notebook_id, owner=request.user)
    context = {
        'notebook': notebook,
        'tags': Tag.objects.filter(created_by=request.user)
    }
    return render(request, 'users/notebook_detail.html', context)

@login_required
def profile_view(request):
    context = {
        'notebooks': Notebook.objects.filter(owner=request.user),
        'notes': Note.objects.filter(owner=request.user),
        'tags': Tag.objects.filter(created_by=request.user)
    }
    return render(request, 'users/profile.html', context)

@login_required
def notebooks_view(request):
    """View for displaying all notebooks."""
    notebooks = Notebook.objects.filter(owner=request.user)
    notes = Note.objects.filter(owner=request.user)
    tags = Tag.objects.filter(created_by=request.user)
    
    context = {
        'notebooks': notebooks,
        'notes': notes.order_by('-updated_at'),
        'tags': tags
    }
    return render(request, 'users/notebooks.html', context)

@login_required
def tags_view(request):
    """View for displaying all tags."""
    notebooks = Notebook.objects.filter(owner=request.user)
    notes = Note.objects.filter(owner=request.user)
    tags = Tag.objects.filter(created_by=request.user)
    
    context = {
        'notebooks': notebooks,
        'notes': notes.order_by('-updated_at'),
        'tags': tags
    }
    return render(request, 'users/tags.html', context)

class RegisterView(APIView):
    permission_classes = [AllowAny]  # Allow anyone to register
    throttle_classes = [CustomAnonRateThrottle]
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    @rate_limit(requests=3, interval=60)
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'User registered successfully!',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request):
        serializer = UserProfileSerializer(request.user.profile)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserProfileSerializer(
            request.user.profile,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
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
