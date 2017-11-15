from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthenticatedAndReadOnly(BasePermission):
    """
    Allows read-only access only to authenticated users.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.method in SAFE_METHODS
        )
