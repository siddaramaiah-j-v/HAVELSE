from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import User

@receiver(user_logged_in,sender=User)
def cancel_deactivation_on_login(sender,request,user,**kwargs):
    if user.profile.deactivated_at:
        user.profile.deactivated_at=None
        user.profile.save()