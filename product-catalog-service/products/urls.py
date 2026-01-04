from django.urls import path
from .views import ProductListCreateView, ProductDetailUpdateDeleteView

urlpatterns = [
    path("", ProductListCreateView.as_view(), name="product-list-create"),
    path("<slug:slug>", ProductDetailUpdateDeleteView.as_view(), name="product-detail-update-delete"),
]
