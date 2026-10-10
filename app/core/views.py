"""
Core views for app
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def health_check(request):
    """Check the health of the application."""
    return Response({'healthy': True})
