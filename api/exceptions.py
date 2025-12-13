"""
Custom Exceptions for API
"""
from rest_framework.exceptions import APIException
from rest_framework import status


class ValidationError(APIException):
    """Custom validation error"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Validation error'
    default_code = 'validation_error'


class NotFoundError(APIException):
    """Custom not found error"""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Resource not found'
    default_code = 'not_found'


class UnauthorizedError(APIException):
    """Custom unauthorized error"""
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Unauthorized access'
    default_code = 'unauthorized'


class ForbiddenError(APIException):
    """Custom forbidden error"""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Access forbidden'
    default_code = 'forbidden'

