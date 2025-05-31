from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView,
    ProtectedView,
    NotebookViewSet,
    NoteViewSet,
    TagViewSet,
    UserProfileView
)

router = DefaultRouter()
router.register(r'notebooks', NotebookViewSet, basename='notebook')
router.register(r'notes', NoteViewSet, basename='note')
router.register(r'tags', TagViewSet, basename='tag')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('', include(router.urls)),
]
