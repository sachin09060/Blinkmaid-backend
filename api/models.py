from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

ROLE_CHOICES = (('customer','Customer'),('maid','Maid'),('admin','Admin'))
GENDER_CHOICES = (('male','Male'),('female','Female'),('other','Other'))

class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=120, blank=True, null=True)
    pincode = models.CharField(max_length=20, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

class MaidProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='maid_profile')
    dob = models.DateField(blank=True, null=True)
    experience_years = models.PositiveIntegerField(default=0)
    services_offered = models.JSONField(default=list, blank=True)
    expected_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    id_proof_type = models.CharField(max_length=100, blank=True, null=True)
    id_proof_number = models.CharField(max_length=200, blank=True, null=True)
    id_proof_image = models.ImageField(upload_to='id_proofs/', blank=True, null=True)
    languages_spoken = models.JSONField(default=list, blank=True)
    bio = models.TextField(blank=True, null=True)
    reference_contact = models.CharField(max_length=200, blank=True, null=True)
    verification_status = models.CharField(max_length=20, default='pending')
    locality = models.CharField(max_length=200, blank=True, null=True)

class State(models.Model):
    name = models.CharField(max_length=200)
    active = models.BooleanField(default=True)
    def __str__(self): return self.name

class City(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='cities')
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='cities/', blank=True, null=True)
    active = models.BooleanField(default=True)
    def __str__(self): return f"{self.name}, {self.state.name}"

class Service(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=200, blank=True, null=True)
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    optional_fields = models.JSONField(default=dict, blank=True)
    active = models.BooleanField(default=True)
    def __str__(self): return self.name

class ServiceOption(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='options')
    duration_label = models.CharField(max_length=50)
    duration_hours = models.IntegerField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self): return f"{self.service.name} - {self.duration_label}"

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    def __str__(self): return self.name

class ContactMessage(models.Model):
    full_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=50)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='unread')
    def __str__(self): return f"{self.full_name} - {self.email}"

class OTPCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    code = models.CharField(max_length=8)
    via = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    def is_valid(self):
        return (not self.used) and (timezone.now() <= self.expires_at)
