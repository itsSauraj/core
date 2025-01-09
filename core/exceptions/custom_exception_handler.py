from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework.views import exception_handler
from rest_framework import status

def handler(exc, context):
    
    response = exception_handler(exc, context)

    if isinstance(exc, AuthenticationFailed):
        response.data = {
            'error': 'Authentication required',
            'detail': exc.detail
        }
        response.status_code = status.HTTP_401_UNAUTHORIZED

    elif isinstance(exc, PermissionDenied):
        response.data = {
            'error': 'Permission Denied',
            'detail': exc.detail
        }
        response.status_code = status.HTTP_403_FORBIDDEN

    return response
