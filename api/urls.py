from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, DashboardView, StateViewSet, CityViewSet, ServiceViewSet, ServiceOptionViewSet, SubscriptionPlanViewSet, MaidAdminViewSet, ContactMessageCreateView, ContactMessageListView, request_otp, verify_otp_and_reset
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'states', StateViewSet, basename='state')
router.register(r'cities', CityViewSet, basename='city')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'service-options', ServiceOptionViewSet, basename='serviceoption')
router.register(r'subscriptions', SubscriptionPlanViewSet, basename='subscription')
router.register(r'maids', MaidAdminViewSet, basename='maid-admin')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('contact/', ContactMessageCreateView.as_view(), name='contact'),
    path('admin/contact-messages/', ContactMessageListView.as_view(), name='admin-contact-list'),
    path('otp/request/', request_otp, name='otp-request'),
    path('otp/verify-reset/', verify_otp_and_reset, name='otp-verify-reset'),
    path('', include(router.urls)),
]
