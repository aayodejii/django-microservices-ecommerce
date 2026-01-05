from django.urls import path
from .views import (
    CartView,
    OrderItemView,
    CheckoutView,
    OrderHistoryView,
)

urlpatterns = [
    path("", CartView.as_view(), name="cart"),
    path("items", OrderItemView.as_view(), name="order-items"),
    path("items/<int:item_id>", OrderItemView.as_view(), name="order-item-detail"),
    path("checkout", CheckoutView.as_view(), name="checkout"),
    path("history", OrderHistoryView.as_view(), name="order-history"),
]
