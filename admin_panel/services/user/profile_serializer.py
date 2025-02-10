from rest_framework import serializers

from admin_panel.models import User


class UpdateUserRequestSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ['employee_id', 'email', 'first_name', 'last_name', 'username',
			'joining_date', 'phone_number', 'avatar', 'birth_date', 'address']
				

class UpdatePasswordRequestSerializer(serializers.Serializer):
	current_password = serializers.CharField(required=True)
	new_password = serializers.CharField(required=True)
	confirm_password = serializers.CharField(required=True)