from rest_framework.permissions import BasePermission, SAFE_METHODS

from api.models import Membership


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


class IsEventManager(BasePermission):
    """
    Global permission check for event manager API call.
    """

    def has_permission(self, request, view):
        try:
            return request.user and (request.user.is_staff or request.user.membership)
        except Membership.DoesNotExist:
            return False


class InvitationPermission(IsEventManager):

    def has_object_permission(self, request, view, invitation):
        try:
            membership = request.user.membership
            return invitation.event in membership.events.all() or invitation.event.organizer == membership.organizer
        except Membership.DoesNotExist:
            return False
