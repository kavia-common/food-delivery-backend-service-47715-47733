from django.contrib.auth import login
from rest_framework import permissions, status, viewsets, mixins
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from .models import Restaurant, MenuItem, Order
from .serializers import (
    SignupSerializer,
    LoginSerializer,
    UserSerializer,
    RestaurantSerializer,
    MenuItemSerializer,
    OrderSerializer,
    OrderStatusUpdateSerializer,
)


# PUBLIC_INTERFACE
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health(request):
    """Health check endpoint.
    Returns 200 with a JSON message if the server is up.
    """
    return Response({"message": "Server is up!"})


class IsOwner(permissions.BasePermission):
    """Allow access only to the owner of an object (Order.user)."""
    def has_object_permission(self, request, view, obj):
        return getattr(obj, "user_id", None) == getattr(request.user, "id", None)


# PUBLIC_INTERFACE
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def signup(request):
    """User signup endpoint.
    Request body: {username, email, password}
    Returns: created user (id, username, email)
    """
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# PUBLIC_INTERFACE
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """User login endpoint using session auth (no tokens).
    Request body: {username, password}
    Returns: user info if credentials valid and sets session cookie.
    """
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data["user"]
    login(request, user)
    return Response(UserSerializer(user).data, status=status.HTTP_200_OK)


class RestaurantViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only endpoints for restaurants (list/retrieve)."""
    queryset = Restaurant.objects.filter(is_active=True).order_by("name")
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.AllowAny]


class MenuItemViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only endpoints for menu items. Can filter by restaurant via query param restaurant=<id>."""
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = MenuItem.objects.filter(available=True).select_related("restaurant").order_by("restaurant_id", "name")
        restaurant_id = self.request.query_params.get("restaurant")
        if restaurant_id:
            qs = qs.filter(restaurant_id=restaurant_id)
        return qs


class OrderViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    """Order endpoints: create order, list own orders, retrieve order, update status (admin-only or future staff)."""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related("restaurant").prefetch_related("items")

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["patch"], serializer_class=OrderStatusUpdateSerializer, permission_classes=[permissions.IsAuthenticated])
    def status(self, request, pk=None):
        """Update order status; currently restricts to the order owner for simplicity."""
        order = self.get_object()
        # In a real system, would restrict to staff/restaurant users.
        serializer = OrderStatusUpdateSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(OrderSerializer(order, context={"request": request}).data)
