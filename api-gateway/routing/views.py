import requests
import re
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.conf import settings

logger = logging.getLogger(__name__)


class ProxyView(APIView):
    """
    Base class that forwards HTTP requests to backend microservices.
    Each subclass sets its own service_url to route to different services.
    """
    service_url = None
    permission_classes = [AllowAny]

    def _is_safe_path(self, path):
        if not path:
            return True
        if '..' in path or path.startswith('/'):
            return False
        if any(prefix in path.lower() for prefix in ['http://', 'https://', 'ftp://']):
            return False
        if not re.match(r'^[a-zA-Z0-9/_.-]+$', path):
            return False
        return True

    def forward_request(self, request, path=""):
        if not self.service_url:
            return Response(
                {"error": "Service URL not configured"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        if not self._is_safe_path(path):
            logger.warning(f"Blocked unsafe path: {path}")
            return Response(
                {"error": "Invalid request path"},
                status=status.HTTP_400_BAD_REQUEST
            )

        target_url = f"{self.service_url}/api/{path}"

        headers = {}
        if request.auth:
            headers['Authorization'] = request.META.get('HTTP_AUTHORIZATION', '')

        try:
            if request.method == 'GET':
                response = requests.get(
                    target_url,
                    params=request.query_params,
                    headers=headers,
                    timeout=30
                )
            elif request.method == 'POST':
                response = requests.post(
                    target_url,
                    data=request.data,
                    headers=headers,
                    timeout=30
                )
            elif request.method == 'PUT':
                response = requests.put(
                    target_url,
                    data=request.data,
                    headers=headers,
                    timeout=30
                )
            elif request.method == 'DELETE':
                response = requests.delete(
                    target_url,
                    headers=headers,
                    timeout=30
                )
            else:
                return Response(
                    {"error": "Method not allowed"},
                    status=status.HTTP_405_METHOD_NOT_ALLOWED
                )

            try:
                data = response.json() if response.content else {}
            except ValueError:
                logger.error(f"Invalid JSON from {target_url}")
                data = {"error": "Invalid response from service"}
                return Response(data, status=status.HTTP_502_BAD_GATEWAY)

            return Response(data, status=response.status_code)

        except requests.exceptions.ConnectionError:
            return Response(
                {"error": "Service unavailable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except requests.exceptions.Timeout:
            return Response(
                {"error": "Service timeout"},
                status=status.HTTP_504_GATEWAY_TIMEOUT
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get(self, request, path=""):
        return self.forward_request(request, path)

    def post(self, request, path=""):
        return self.forward_request(request, path)

    def put(self, request, path=""):
        return self.forward_request(request, path)

    def delete(self, request, path=""):
        return self.forward_request(request, path)


class UserServiceProxy(ProxyView):
    """Routes requests to the User Authentication Service"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service_url = settings.USER_SERVICE_URL


class ProductServiceProxy(ProxyView):
    """Routes requests to the Product Catalog Service"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service_url = settings.PRODUCT_SERVICE_URL


class OrderServiceProxy(ProxyView):
    """Routes requests to the Order Management Service"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service_url = settings.ORDER_SERVICE_URL


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "status": "healthy",
            "service": "api-gateway",
            "version": "1.0.0"
        })
