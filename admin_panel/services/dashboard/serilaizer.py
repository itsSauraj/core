from rest_framework import serializers

class InfoCardSerializer(serializers.Serializer):
  title = serializers.CharField()
  count = serializers.IntegerField()

class CourseCompletionStatusSerializer(serializers.Serializer):
  course = serializers.CharField()
  enrolled = serializers.IntegerField()
  completed = serializers.IntegerField()
  in_progress = serializers.IntegerField()
  not_started = serializers.IntegerField()