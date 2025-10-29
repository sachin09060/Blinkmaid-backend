from django.contrib import admin
from .models import User, MaidProfile, State, City, Service, ServiceOption, SubscriptionPlan, ContactMessage, OTPCode
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (('Additional', {'fields': ('role','phone_number','address','city','pincode','profile_image','gender')}),)
    list_display = ('email','username','role','phone_number','is_staff','is_active')

admin.site.register(MaidProfile)
admin.site.register(State)
admin.site.register(City)
admin.site.register(Service)
admin.site.register(ServiceOption)
admin.site.register(SubscriptionPlan)
admin.site.register(ContactMessage)
admin.site.register(OTPCode)
