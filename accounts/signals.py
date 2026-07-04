from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Profile
from django.contrib.auth import get_user_model


@receiver(post_save, sender=User)
def created_user(sender, instance , created , **kwargs):

    User = get_user_model

    if created:
        Profile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()