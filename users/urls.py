from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from .views import (
    RegisterView,
    ProtectedView,
    NotebookViewSet,
    NoteViewSet,
    TagViewSet,
    UserProfileView,
    register_view,
    login_view,
    home_view,
    notebook_detail_view,
    profile_view,
    notebooks_view,
    tags_view
)

# API Router
router = DefaultRouter()
router.register('notebooks', NotebookViewSet, basename='notebook')
router.register('notes', NoteViewSet, basename='note')
router.register('tags', TagViewSet, basename='tag')

# Template View URLs
template_urlpatterns = [
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('profile/', profile_view, name='profile'),
    path('notebooks/', notebooks_view, name='notebooks'),
    path('notebooks/<int:notebook_id>/', notebook_detail_view, name='notebook_detail'),
    path('tags/', tags_view, name='tags'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
]

# API URLs
api_urlpatterns = [
    path('api/register/', RegisterView.as_view(), name='api_register'),
    path('api/protected/', ProtectedView.as_view(), name='api_protected'),
    path('api/profile/', UserProfileView.as_view(), name='api_profile'),
    path('api/', include(router.urls)),
]

urlpatterns = template_urlpatterns + api_urlpatterns
