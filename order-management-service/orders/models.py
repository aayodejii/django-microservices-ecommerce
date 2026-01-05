from django.db import models


class Order(models.Model):
    STATUS_CHOICES = [
        ('cart', 'Cart'),
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user_id = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='cart')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - User {self.user_id} - {self.status}"

    class Meta:
        ordering = ["-created_at"]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_id = models.IntegerField()
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OrderItem {self.id} - Product {self.product_id} x {self.quantity}"

    class Meta:
        ordering = ["id"]
