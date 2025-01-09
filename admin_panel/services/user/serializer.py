import re

from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers

from admin_panel.models import User

class CreateUserRequestSerializer(ModelSerializer):
		
		"""
		Takes data from the request and validates it
		data = {
			"username": "johndoe",
			"first_name": "John",
			"last_name": "Doe"
			"email": "example@mail.com",
			"password": "password",
			"confirm_password": "password"
		}
		"""

		confirm_password = serializers.CharField(write_only=True)
		role = serializers.CharField(write_only=True, required=False)

		class Meta:
			model = User
			fields = ['email', 'password', 'confirm_password' , 'first_name', 'last_name', "username", "role"]

		def validate(self, data):
			password_regex = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$"
			
			if not re.match(password_regex, data['password']):
				raise serializers.ValidationError(
					"Password must be at least 6 characters long, contain at least one uppercase letter, one lowercase letter, and one number.",
					code='password_invalid'
				)

			if data['password'] != data['confirm_password']:
				raise serializers.ValidationError("Passwords do not match", code='password_mismatch')
			
			if data['role'].capitalize() not in ['', 'Mentor', 'Trainee']:
				raise serializers.ValidationError("Invalid role", code='invalid_role')

			return data
		
class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
				
class ResponseUserSerializer(Serializer):
    class Meta:
        model = User
        exclude = ['password', 'deleted_at', 'created_by', 'updated_at']