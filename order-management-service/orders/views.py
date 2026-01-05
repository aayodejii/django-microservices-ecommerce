from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from decimal import Decimal
from .models import Order, OrderItem
from .serializers import (
    OrderSerializer,
    AddItemSerializer,
    UpdateOrderSerializer,
)


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id
        order = Order.objects.filter(user_id=user_id, status='cart').first()
        if not order:
            return Response({"message": "Cart is empty"}, status=status.HTTP_200_OK)
        serializer = OrderSerializer(order)
        return Response(serializer.data)


class OrderItemView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddItemSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_id = request.user.id
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']
        price = serializer.validated_data['price']

        order, created = Order.objects.get_or_create(
            user_id=user_id,
            status='cart'
        )

        order_item, item_created = OrderItem.objects.get_or_create(
            order=order,
            product_id=product_id,
            defaults={'quantity': quantity, 'price': price}
        )

        if not item_created:
            order_item.quantity += quantity
            order_item.save()

        order.total = sum(item.price * item.quantity for item in order.items.all())
        order.save()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    def put(self, request, item_id):
        serializer = UpdateOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_id = request.user.id
        quantity = serializer.validated_data['quantity']

        order = Order.objects.filter(user_id=user_id, status='cart').first()
        if not order:
            return Response({"error": "No active cart found"}, status=status.HTTP_404_NOT_FOUND)

        order_item = get_object_or_404(OrderItem, id=item_id, order=order)
        order_item.quantity = quantity
        order_item.save()

        order.total = sum(item.price * item.quantity for item in order.items.all())
        order.save()

        return Response(OrderSerializer(order).data)

    def delete(self, request, item_id):
        user_id = request.user.id
        order = Order.objects.filter(user_id=user_id, status='cart').first()

        if not order:
            return Response({"error": "No active cart found"}, status=status.HTTP_404_NOT_FOUND)

        order_item = get_object_or_404(OrderItem, id=item_id, order=order)
        order_item.delete()

        order.total = sum(item.price * item.quantity for item in order.items.all())
        order.save()

        return Response(OrderSerializer(order).data)


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = request.user.id
        order = Order.objects.filter(user_id=user_id, status='cart').first()

        if not order or not order.items.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        order.status = 'completed'
        order.save()

        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)


class OrderHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id
        orders = Order.objects.filter(user_id=user_id, status='completed')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
