import re

from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers

from admin_panel.models import User

class CreateAdminRequestSerializer(ModelSerializer):
		
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

		class Meta:
			model = User
			fields = ['email', 'password', 'confirm_password' , 'first_name', 'last_name', "username"]

		def validate(self, data):
			password_regex = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$"
			
			if not re.match(password_regex, data['password']):
				raise serializers.ValidationError(
					"Password must be at least 6 characters long, contain at least one uppercase letter, one lowercase letter, and one number.",
					code='password_invalid'
				)

			if data['password'] != data['confirm_password']:
				raise serializers.ValidationError("Passwords do not match", code='password_mismatch')
			return data

class UserSerializer(ModelSerializer):
		class Meta:
			model = User
			fields = '__all__'