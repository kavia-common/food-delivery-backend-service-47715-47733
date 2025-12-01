from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import Restaurant, MenuItem, Order, OrderItem

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user info."""
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class SignupSerializer(serializers.ModelSerializer):
    """Signup serializer validating password and creating a user."""
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email") or "",
            password=validated_data["password"],
        )


class LoginSerializer(serializers.Serializer):
    """Serializer for login."""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs.get("username"), password=attrs.get("password"))
        if not user:
            raise serializers.ValidationError("Invalid username or password")
        attrs["user"] = user
        return attrs


class MenuItemSerializer(serializers.ModelSerializer):
    """Serializer for MenuItem."""
    class Meta:
        model = MenuItem
        fields = ["id", "restaurant", "name", "description", "price", "available"]


class RestaurantSerializer(serializers.ModelSerializer):
    """Serializer for Restaurant with nested menu items optional."""
    menu_items = MenuItemSerializer(many=True, read_only=True)

    class Meta:
        model = Restaurant
        fields = ["id", "name", "description", "address", "is_active", "menu_items"]


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items."""
    menu_item_detail = MenuItemSerializer(source="menu_item", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "menu_item", "menu_item_detail", "quantity", "unit_price"]
        read_only_fields = ["unit_price"]


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for order with nested items and derived totals."""
    items = OrderItemSerializer(many=True)
    user = UserSerializer(read_only=True)
    restaurant_detail = RestaurantSerializer(source="restaurant", read_only=True)

    class Meta:
        model = Order
        fields = ["id", "user", "restaurant", "restaurant_detail", "status", "total_amount", "items", "created_at", "updated_at"]
        read_only_fields = ["status", "total_amount", "created_at", "updated_at"]

    def validate(self, attrs):
        # Validate that all items belong to the same restaurant when creating
        request = self.context.get("request")
        if request and request.method == "POST":
            items = self.initial_data.get("items") or []
            restaurant_id = attrs.get("restaurant")
            if not items:
                raise serializers.ValidationError("Order must contain at least one item.")
            if restaurant_id is None:
                raise serializers.ValidationError("Restaurant is required.")
            menu_ids = [i.get("menu_item") for i in items]
            if MenuItem.objects.filter(pk__in=menu_ids).exclude(restaurant_id=restaurant_id.id if hasattr(restaurant_id, 'id') else restaurant_id).exists():
                raise serializers.ValidationError("All menu items must belong to the specified restaurant.")
        return attrs

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        user = self.context["request"].user
        order = Order.objects.create(user=user, **validated_data)
        # Create items and set unit_price from menu
        for item in items_data:
            menu = MenuItem.objects.get(pk=item["menu_item"].id if hasattr(item["menu_item"], "id") else item["menu_item"])
            qty = int(item.get("quantity", 1))
            OrderItem.objects.create(order=order, menu_item=menu, quantity=qty, unit_price=menu.price)
        order.recalc_total()
        return order


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer to update order status."""
    class Meta:
        model = Order
        fields = ["status"]
