from rest_framework import generics, viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from .models import MaidProfile, State, City, Service, ServiceOption, SubscriptionPlan, ContactMessage, OTPCode
from .serializers import (UserRegisterSerializer, UserSerializer, MaidProfileSerializer, StateSerializer, CitySerializer, ServiceSerializer, ServiceOptionSerializer, SubscriptionPlanSerializer, ContactMessageSerializer, OTPRequestSerializer)
from .permissions import IsAdminRole
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils import timezone
from datetime import timedelta
import random
from django.core.mail import send_mail

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

class DashboardView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return self.request.user
    def get(self, request, *args, **kwargs):
        user = self.get_object()
        data = UserSerializer(user).data
        if user.role == 'admin':
            data['counts'] = {
                'total_customers': User.objects.filter(role='customer').count(),
                'total_maids': User.objects.filter(role='maid').count(),
                'pending_maids': MaidProfile.objects.filter(verification_status='pending').count(),
                'contact_messages': ContactMessage.objects.count()
            }
        elif user.role == 'maid':
            profile = getattr(user, 'maid_profile', None)
            data['profile'] = MaidProfileSerializer(profile).data if profile else {}
        else:
            data['message'] = 'Customer dashboard summary'
        return Response(data)

class StateViewSet(viewsets.ModelViewSet):
    queryset = State.objects.all()
    serializer_class = StateSerializer
    permission_classes = [IsAuthenticated & IsAdminRole]

class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [IsAuthenticated & IsAdminRole]

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated & IsAdminRole]

class ServiceOptionViewSet(viewsets.ModelViewSet):
    queryset = ServiceOption.objects.all()
    serializer_class = ServiceOptionSerializer
    permission_classes = [IsAuthenticated & IsAdminRole]

class SubscriptionPlanViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAuthenticated & IsAdminRole]

class MaidAdminViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MaidProfile.objects.all()
    serializer_class = MaidProfileSerializer
    permission_classes = [IsAuthenticated & IsAdminRole]
    @action(detail=True, methods=['post'])
    def set_status(self, request, pk=None):
        profile = self.get_object()
        status_val = request.data.get('status')
        if status_val not in ('pending','approved','rejected'):
            return Response({'detail':'invalid status'}, status=400)
        profile.verification_status = status_val
        profile.save()
        return Response({'detail':'status updated'})

class ContactMessageCreateView(generics.CreateAPIView):
    serializer_class = ContactMessageSerializer
    permission_classes = [AllowAny]

class ContactMessageListView(generics.ListAPIView):
    queryset = ContactMessage.objects.all().order_by('-submitted_at')
    serializer_class = ContactMessageSerializer
    permission_classes = [IsAuthenticated & IsAdminRole]

@api_view(['POST'])
@permission_classes([AllowAny])
def request_otp(request):
    ser = OTPRequestSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    identifier = ser.validated_data['identifier']
    via = ser.validated_data['via']
    try:
        if via == 'phone':
            user = User.objects.get(phone_number=identifier)
        else:
            user = User.objects.get(email=identifier)
    except User.DoesNotExist:
        return Response({'detail':'No user found with provided identifier'}, status=404)
    code = f"{random.randint(100000,999999)}"
    expires_at = timezone.now() + timedelta(minutes=10)
    otp = OTPCode.objects.create(user=user, code=code, via=via, expires_at=expires_at)
    if via == 'email':
        send_mail('Your Blinkmaid OTP', f'Your OTP is {code}', 'no-reply@blinkmaid.com', [user.email])
    else:
        print(f'OTP for {user.phone_number}: {code}')
    return Response({'detail':'OTP sent if user exists.'})

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp_and_reset(request):
    identifier = request.data.get('identifier')
    via = request.data.get('via')
    code = request.data.get('code')
    new_password = request.data.get('new_password')
    if not all([identifier, via, code, new_password]):
        return Response({'detail':'Missing fields'}, status=400)
    try:
        if via == 'phone':
            user = User.objects.get(phone_number=identifier)
        else:
            user = User.objects.get(email=identifier)
    except User.DoesNotExist:
        return Response({'detail':'User not found'}, status=404)
    otp_qs = OTPCode.objects.filter(user=user, code=code, used=False).order_by('-created_at')
    if not otp_qs.exists():
        return Response({'detail':'Invalid or used OTP'}, status=400)
    otp = otp_qs.first()
    if not otp.is_valid():
        return Response({'detail':'OTP expired or invalid'}, status=400)
    user.set_password(new_password)
    user.save()
    otp.used = True
    otp.save()
    return Response({'detail':'Password reset successful.'})
