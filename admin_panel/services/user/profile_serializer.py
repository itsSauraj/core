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

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class VerifyOTPSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    otp = serializers.CharField(min_length=6, max_length=6)

class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=6)
    confirm_password = serializers.CharField(min_length=6)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        return data