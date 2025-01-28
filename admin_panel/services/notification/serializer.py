from rest_framework import serializers
from admin_panel.models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'sender', 'recipient', 'title', 'message', 'type', 'read', 'created_at']
        read_only_fields = ['created_at']