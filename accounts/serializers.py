from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password
from transactions.models import Transfer

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfer
        fields = '__all__'

User = get_user_model()

class CustomLoginSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user

        # 🚫 Block if not approved
        if not user.is_approved:
            raise serializers.ValidationError(
                "Account not approved by admin."
            )

        # 🚫 Block if restricted
        if user.is_restricted:
            raise serializers.ValidationError(
                "Account is restricted."
            )

        return data

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'telephone',
            'full_name',
            'address',
            'country',
            'password'
        ]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.is_approved = False
        user.save()
        return user
    
class UserSerializer(serializers.ModelSerializer):
    has_pin = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "telephone",
            "full_name",
            "address",
            "country",
            "balance",
            "profile_picture",
            "has_pin",  # ✅ ADD THIS
        ]

    def get_has_pin(self, obj):
        return bool(obj.transaction_pin)
        
class CreatePinSerializer(serializers.Serializer):
    pin = serializers.CharField(max_length=6)

    def validate_pin(self, value):
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError("PIN must be 6 digits.")
        return value

    def save(self, user):
        if user.transaction_pin:
            raise serializers.ValidationError("PIN already set.")

        user.transaction_pin = make_password(self.validated_data["pin"])
        user.save()
        return user
    
class VerifyPinSerializer(serializers.Serializer):
    pin = serializers.CharField(max_length=6)

    def validate(self, attrs):
        user = self.context["user"]

        if not user.transaction_pin:
            raise serializers.ValidationError("No PIN set.")

        if not check_password(attrs["pin"], user.transaction_pin):
            raise serializers.ValidationError("Invalid PIN.")

        return attrs