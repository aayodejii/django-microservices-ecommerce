from django_filters import rest_framework as filters
from .models import Product


class ProductFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    min_price = filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='price', lookup_expr='lte')
    in_stock = filters.BooleanFilter(method='filter_in_stock')

    class Meta:
        model = Product
        fields = ['search', 'min_price', 'max_price', 'in_stock']

    def filter_search(self, queryset, name, value):
        return queryset.filter(name__icontains=value) | queryset.filter(description__icontains=value)

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(inventory__gt=0)
        return queryset
