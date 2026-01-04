from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from .models import Product
from .serializers import ProductSerializer, ProductCreateUpdateSerializer
from .filters import ProductFilter


class ProductListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request):
        products = Product.objects.all()
        filterset = ProductFilter(request.GET, queryset=products)
        if filterset.is_valid():
            products = filterset.qs
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            return Response(
                ProductSerializer(product).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailUpdateDeleteView(APIView):
    def get_permissions(self):
        if self.request.method in ["PUT", "DELETE"]:
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        serializer = ProductCreateUpdateSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(ProductSerializer(product).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
