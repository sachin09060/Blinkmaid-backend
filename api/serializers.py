from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import MaidProfile, State, City, Service, ServiceOption, SubscriptionPlan, ContactMessage, OTPCode
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    role = serializers.ChoiceField(choices=(('customer','Customer'),('maid','Maid'),('admin','Admin')), default='customer')
    class Meta:
        model = User
        fields = ('id','username','email','password','role','phone_number','address','city','pincode','profile_image','gender','first_name','last_name')
    def create(self, validated_data):
        password = validated_data.pop('password')
        username = validated_data.get('username') or validated_data.get('email').split('@')[0]
        user = User(**validated_data)
        user.username = username
        user.set_password(password)
        user.save()
        if user.role == 'maid':
            MaidProfile.objects.create(user=user)
        return user

class MaidProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaidProfile
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    maid_profile = MaidProfileSerializer(read_only=True)
    class Meta:
        model = User
        fields = ('id','email','username','role','phone_number','address','city','pincode','profile_image','gender','first_name','last_name','maid_profile')

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = '__all__'

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'

class ServiceOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceOption
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    options = ServiceOptionSerializer(many=True, read_only=True)
    class Meta:
        model = Service
        fields = '__all__'

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'

class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = '__all__'

class OTPRequestSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    via = serializers.ChoiceField(choices=(('phone','phone'),('email','email')))
