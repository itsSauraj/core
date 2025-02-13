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
    return {
      "id": str(obj.sender.id),
      "name": obj.sender.get_full_name(),
      "avatar": obj.sender.avatar.url if obj.sender.avatar else None
    } if obj.sender else None

  def get_recipient(self, obj):
    return str(obj.recipient.id) if obj.recipient else None

class CreateNotificationSerializer(serializers.ModelSerializer):
  class Meta:
    model = Notification
    fields = ['recipient', 'title', 'message', 'type']