from django.db import models
from django.contrib.auth.models import User
# Create your models here.
CHOICES= [
    ('M', 'male'),
    ('F', 'female'),
    ('O', 'prefer not to say'),
]

class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=10)
    gender=models.CharField(choices=CHOICES,blank=True)
    bio=models.CharField(max_length=50,blank=True)
    email = models.EmailField(unique=True)
    phone = models.IntegerField(unique=True)
    image=models.ImageField(default='profile.png',upload_to='profile_pictures/')
    deactivated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.user)
