from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Object-level: only the owning user may read or write."""

    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id


class IsOwnerOrPublicReadOnly(permissions.BasePermission):
    """Owner has full access. Anyone authenticated may read a public object."""

    def has_object_permission(self, request, view, obj):
        if obj.user_id == request.user.id:
            return True
        if request.method in permissions.SAFE_METHODS:
            return bool(obj.is_public)
        return False
