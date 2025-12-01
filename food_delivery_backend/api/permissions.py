from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Order ownership permission placeholder (not used directly)."""
    def has_object_permission(self, request, view, obj):
        return getattr(obj, "user_id", None) == getattr(request.user, "id", None)
