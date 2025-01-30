from rest_framework import serializers

class InfoCardSerializer(serializers.Serializer):
  title = serializers.CharField()
  count = serializers.IntegerField()