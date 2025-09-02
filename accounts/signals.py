from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile

# we want to create a profile for each user that has been created
User_Model = settings.AUTH_USER_MODEL
@receiver(post_save, sender=User_Model) #receiver catches a signal (now, from a post_save that the user model sends everytime it saves an instance)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)