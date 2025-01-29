# notifications/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from admin_panel.models import Notification
from admin_panel.services.notification.serializer import NotificationSerializer, CreateNotificationSerializer
from admin_panel.services.notification.service import NotificationService

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)
    
    @action(detail=False, methods=['post'])
    def send(self, request):
        sender = request.user

        serializer = CreateNotificationSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data

        # recipient = data.get('recipient')
        recipient = request.user
        message = data.get('message')
        notification_type = data.get('type', 'info')
        
        notification = NotificationService.send_notification(sender, recipient, message, notification_type)
        return Response(self.serializer_class(notification).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        self.get_queryset().update(read=True)
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.read = True
        notification.save()
        return Response(status=status.HTTP_200_OK)
