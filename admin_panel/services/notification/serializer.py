from rest_framework import serializers
from admin_panel.models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(format='hex', read_only=True)
    sender = serializers.SerializerMethodField()
    recipient = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'sender', 'recipient', 'title', 'message', 'type', 'read', 'created_at']
        read_only_fields = ['created_at']

    def get_sender(self, obj):
        return str(obj.sender.id) if obj.sender else None

    def get_recipient(self, obj):
        return str(obj.recipient.id) if obj.recipient else None

class CreateNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['recipient', 'title', 'message', 'type']