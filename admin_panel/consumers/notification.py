import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from admin_panel.models import Notification
from admin_panel.services.notification.serializer import NotificationSerializer

class NotificationConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        self.user_id = None
        self.room_group_name = ""
        super().__init__(*args, **kwargs)

    async def connect(self):
        self.user_id = self.scope["user_id"]
        self.room_group_name = f"user_{self.user_id}_notifications"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        unread_notifications = await self.get_unread_notifications()
        if unread_notifications:
            await self.send(text_data=json.dumps(unread_notifications))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        command = data.get('command')

        if command == 'mark_as_read':
            notification_id = data.get('notification_id')
            if notification_id:
                await self.mark_notification_as_read(notification_id)
                await self.send(text_data=json.dumps({
                    'type': 'notification_marked_read',
                    'notification_id': notification_id
                }))

    async def notification_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_notification',
            'notification': event['notification']
        }))

    @database_sync_to_async
    def get_unread_notifications(self):
        notifications = Notification.objects.filter(
            recipient_id=self.user_id,
            read=False
        ).order_by('-created_at')
        return {
            'type': 'initial_notifications',
            'notifications': NotificationSerializer(notifications, many=True).data
        }

    @database_sync_to_async
    def mark_notification_as_read(self, notification_id):
        try:
            notification = Notification.objects.get(
                id=notification_id,
                recipient_id=self.user_id
            )
            notification.read = True
            notification.save()
            return True
        except Notification.DoesNotExist:
            return False