"""
Custom Middleware for Error Handling and Logging
"""
import logging
import traceback
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(MiddlewareMixin):
    """Middleware to handle errors globally"""
    
    def process_exception(self, request, exception):
        """Handle exceptions and return JSON response"""
        logger.error(
            f"Exception in {request.path}: {str(exception)}",
            exc_info=True,
            extra={
                'request_path': request.path,
                'request_method': request.method,
                'user': str(request.user) if hasattr(request, 'user') else 'Anonymous',
            }
        )
        
        # Return JSON error response for API requests
        if request.path.startswith('/api/'):
            return JsonResponse({
                'error': str(exception),
                'code': type(exception).__name__,
                'path': request.path,
            }, status=500)
        
        # Let Django handle other exceptions
        return None


class RequestLoggingMiddleware(MiddlewareMixin):
    """Middleware to log API requests"""
    
    def process_request(self, request):
        """Log incoming requests"""
        if request.path.startswith('/api/'):
            logger.info(
                f"{request.method} {request.path}",
                extra={
                    'method': request.method,
                    'path': request.path,
                    'user': str(request.user) if hasattr(request, 'user') else 'Anonymous',
                }
            )

