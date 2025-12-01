from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import health, signup, login_view, RestaurantViewSet, MenuItemViewSet, OrderViewSet

router = DefaultRouter()
router.register(r"restaurants", RestaurantViewSet, basename="restaurant")
router.register(r"menu-items", MenuItemViewSet, basename="menuitem")
router.register(r"orders", OrderViewSet, basename="order")

urlpatterns = [
    path('health/', health, name='Health'),
    path('auth/signup/', signup, name='Signup'),
    path('auth/login/', login_view, name='Login'),
    path('', include(router.urls)),
]
