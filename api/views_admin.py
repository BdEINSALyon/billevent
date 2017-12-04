# This file contains routes only allowed for a membership user
# Permission must be ensure by link between an organization and a user
# User and Organization is a One to Many relationship. A user can have only one organization.
from rest_framework import viewsets

from api import serializers_admin as serializers, permissions
from api.models import Event, Organizer, Invitation


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.EventSerializer
    permission_classes = [permissions.IsEventManager]

    def get_queryset(self):
        return (Event.objects.filter(organizer__membership__user=self.request.user) |
                Event.objects.filter(membership__user=self.request.user))


class OrganizerViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.OrganizerSerializer
    permission_classes = [permissions.IsEventManager]

    def get_queryset(self):
        return Organizer.objects.filter(membership__user=self.request.user)


class InvitationViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.InvitationSerializer
    permission_classes = [permissions.InvitationPermission]

    def get_queryset(self):
        return Invitation.objects.filter(event__organizer__membership__user=self.request.user) | \
               Invitation.objects.filter(event__membership__user=self.request.user)
