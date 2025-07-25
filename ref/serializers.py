from rest_framework import serializers
from ref.models import User
import time

class PhoneAuthSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    
    def validate_phone(self, value):
        # Простая валидация номера телефона
        if not value.startswith('+') or not value[1:].isdigit():
            raise serializers.ValidationError("Номер телефона должен быть в формате +79123456789")
        return value

class CodeAuthSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    code = serializers.CharField(max_length=4)

class UserProfileSerializer(serializers.ModelSerializer):
    referred_users = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['phone', 'invite_code', 'activated_invite_code', 'referred_users']
    
    def get_referred_users(self, obj):
        return list(User.objects.filter(activated_invite_code=obj.invite_code).values_list('phone', flat=True))

class InviteCodeSerializer(serializers.Serializer):
    invite_code = serializers.CharField(max_length=6)