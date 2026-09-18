from rest_framework import permissions


class IsApproved(permissions.BasePermission):
    """Mirrors the web app's admin-approval gate; defense in depth behind the token view."""

    message = "Your account is pending admin approval."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_approved
        )


class IsOwner(permissions.BasePermission):
    """Object-level: only the owning user may read or write."""

    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id


class IsOwnerOrPublicReadOnly(permissions.BasePermission):
    """Owner has full access. Anyone authenticated may read a public or global object."""

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if obj.user_id is None:
            # Global/seeded object (no owner): readable by any authenticated user.
            return request.method in permissions.SAFE_METHODS
        if obj.user_id == request.user.id:
            return True
        if request.method in permissions.SAFE_METHODS:
            return bool(obj.is_public)
        return False


class IsBatchOwnerOrPublicReadOnly(permissions.BasePermission):
    """Like IsOwnerOrPublicReadOnly, but for objects related via `.batch`."""

    def has_permission(self, request, view):
        # Write access to a specific batch is enforced by the serializer, whose
        # `batch` queryset is restricted to the requesting user's batches. Doing
        # the check here as well would run before validation and blow up (500)
        # on a malformed `batch` value instead of yielding a clean 400.
        return True

    def has_object_permission(self, request, view, obj):
        if obj.batch.user_id == request.user.id:
            return True
        if request.method in permissions.SAFE_METHODS:
            return bool(obj.batch.is_public)
        return False
