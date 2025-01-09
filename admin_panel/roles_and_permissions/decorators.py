from functools import wraps
from rest_framework import status
from rest_framework.response import Response
    
def group_required(group_name):
    """
    Decorator to check if the logged-in user belongs to a specific group.

    :param group_name: Name of the required group (or a list of group names).
    :return: View if user belongs to the group, otherwise 403 Forbidden.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Check if user is authenticated and belongs to the group(s)
            if request.user.is_authenticated and (
                request.user.groups.filter(name=group_name).exists()
                if isinstance(group_name, str)
                else request.user.groups.filter(name__in=group_name).exists()
            ):
                return view_func(request, *args, **kwargs)
            return Response("Forbidden", status=status.HTTP_403_FORBIDDEN)
        return _wrapped_view
    return decorator
