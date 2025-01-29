from uuid import UUID

from channels.layers import get_channel_layer

from asgiref.sync import async_to_sync

from admin_panel.models import Notification
from .serializer import NotificationSerializer

class NotificationService:
    @staticmethod
    def send_notification(sender, recipient, title, message, notification_type='info'):
        # Create notification in database
        notification = Notification.objects.create(
            sender=sender,
            recipient=recipient,
            title=title,
            message=message,
            type=notification_type
        )
        
        serialized_notification = NotificationSerializer(notification).data

        # Send to websocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{recipient.id}_notifications",
            {
                "type": "notification_message",
                "notification": serialized_notification
            }
        )
        
        return notification
