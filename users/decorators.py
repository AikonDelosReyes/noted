from django.core.cache import cache
from rest_framework.response import Response
from rest_framework import status
from functools import wraps
from django.conf import settings
import time

def rate_limit(requests=5, interval=60):
    """
    Rate limiting decorator that limits the number of requests within a specific timeframe.
    
    Args:
        requests (int): Number of requests allowed
        interval (int): Time window in seconds
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(view_instance, request, *args, **kwargs):
            # Create a unique cache key for each user/IP
            if request.user.is_authenticated:
                cache_key = f'rate_limit_{request.user.id}'
            else:
                cache_key = f'rate_limit_{request.META.get("REMOTE_ADDR")}'
            
            # Get the list of request timestamps from cache
            request_history = cache.get(cache_key, [])
            now = time.time()
            
            # Remove old requests outside the time window
            request_history = [timestamp for timestamp in request_history 
                             if now - timestamp < interval]
            
            # Check if request limit is exceeded
            if len(request_history) >= requests:
                return Response({
                    'error': 'Too many requests',
                    'detail': f'Please wait before making another request. Maximum {requests} requests per {interval} seconds.',
                    'retry_after': int(interval - (now - request_history[0]))
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
            # Add current request timestamp
            request_history.append(now)
            cache.set(cache_key, request_history, interval)
            
            return view_func(view_instance, request, *args, **kwargs)
        return _wrapped_view
    return decorator 