from django.conf import settings
from django.db import models
from django.utils import timezone


class TimestampedModel(models.Model):
    """Abstract base model with created/updated timestamps."""
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Restaurant(TimestampedModel):
    """Restaurant entity representing a vendor on the platform."""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name


class MenuItem(TimestampedModel):
    """A menu item belonging to a restaurant."""
    restaurant = models.ForeignKey(Restaurant, related_name="menu_items", on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.restaurant.name})"


class Order(TimestampedModel):
    """Customer order with status and totals."""
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        PREPARING = "PREPARING", "Preparing"
        OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY", "Out for delivery"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="orders", on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, related_name="orders", on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def recalc_total(self):
        total = sum([oi.quantity * oi.unit_price for oi in self.items.all()])
        self.total_amount = total
        self.save(update_fields=["total_amount", "updated_at"])

    def __str__(self) -> str:
        return f"Order #{self.pk} - {self.user} - {self.restaurant.name}"


class OrderItem(models.Model):
    """Line item in an order."""
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, related_name="order_items", on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        # Ensure unit_price defaults to current MenuItem price if not set
        if self.unit_price is None:
            self.unit_price = self.menu_item.price
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.quantity} x {self.menu_item.name} (Order {self.order_id})"
