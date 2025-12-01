# food-delivery-backend-service-47715-47733

Food delivery backend service using Django and Django REST Framework.

How to run locally:
- Install dependencies: pip install -r food_delivery_backend/requirements.txt
- Run migrations:
  - python food_delivery_backend/manage.py makemigrations
  - python food_delivery_backend/manage.py migrate
- Create a superuser (optional): python food_delivery_backend/manage.py createsuperuser
- Start server: python food_delivery_backend/manage.py runserver 0.0.0.0:3001

Core endpoints (prefix /api/):
- GET /api/health/ -> health check
- POST /api/auth/signup/ -> create user
- POST /api/auth/login/ -> login (session auth)
- GET /api/restaurants/ -> list restaurants
- GET /api/restaurants/{id}/ -> restaurant details (with menu)
- GET /api/menu-items/?restaurant={id} -> list menu items
- POST /api/orders/ -> create order with items
  Example payload:
  {
    "restaurant": 1,
    "items": [{"menu_item": 10, "quantity": 2}]
  }
- GET /api/orders/ -> list my orders
- GET /api/orders/{id}/ -> retrieve my order
- PATCH /api/orders/{id}/status/ -> update order status

Swagger docs: /docs
Redoc: /redoc