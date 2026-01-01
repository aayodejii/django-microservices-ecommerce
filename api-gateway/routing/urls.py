from django.urls import path, re_path
from .views import UserServiceProxy, ProductServiceProxy, OrderServiceProxy, HealthCheckView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),

    re_path(r'^user/(?P<path>.*)$', UserServiceProxy.as_view(), name='user-service'),
    re_path(r'^product(?:s)?/(?P<path>.*)$', ProductServiceProxy.as_view(), name='product-service'),
    re_path(r'^order/(?P<path>.*)$', OrderServiceProxy.as_view(), name='order-service'),
]
