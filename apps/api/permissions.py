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


class IsBatchOwnerOrPublicReadOnly(permissions.BasePermission):
    """Like IsOwnerOrPublicReadOnly, but for objects related via `.batch`."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        batch_id = request.data.get("batch")
        if batch_id is None:
            return True  # let serializer validation reject the missing field
        from apps.batches.models import Batch

        return Batch.objects.filter(pk=batch_id, user=request.user).exists()

    def has_object_permission(self, request, view, obj):
        if obj.batch.user_id == request.user.id:
            return True
        if request.method in permissions.SAFE_METHODS:
            return bool(obj.batch.is_public)
        return False
