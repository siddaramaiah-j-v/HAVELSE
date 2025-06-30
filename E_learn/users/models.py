from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.timezone import timedelta
from django.core.validators import RegexValidator
import string,random
# Create your models here.
CHOICES= [
    ('M', 'male'),
    ('F', 'female'),
    ('O', 'prefer not to say'),
]


phone_validator = RegexValidator(
    regex=r'^(?:\+91[\-\s]?|0)?[6-9]\d{9}$',
    message='Enter a valid phone number.',
    code='invalid_phone'
)



class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    gender=models.CharField(choices=CHOICES,blank=True,max_length=1)
    bio=models.CharField(max_length=50,blank=True)
    phone = models.CharField(max_length=15, unique=True,validators=[phone_validator])
    image=models.ImageField(default='profile.png',upload_to='profile_pictures/')
    deactivated_at = models.DateTimeField(null=True, blank=True)
    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)




class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=[
        ('email_verification', 'Email Verification'),
        ('login', 'Login'),
        ('password_reset', 'Password Reset')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.otp_code:
            self.otp_code = self.generate_otp()
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at


    def generate_otp(self):
        return ''.join(random.choices(string.digits, k=6))

    @classmethod
    def has_exceeded_limit(cls,user, purpose, max_attempts=5, window_minutes=60):
        recent_otp_count = OTP.objects.filter(
            user=user,
            purpose=purpose,
            created_at__gte=timezone.now() - timedelta(minutes=window_minutes)
        ).count()
        return recent_otp_count >= max_attempts

    class Meta:
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]
