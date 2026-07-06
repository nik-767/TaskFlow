from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'username'

    # 4. Fields required when running 'python manage.py createsuperuser'
    REQUIRED_FIELDS = ['email']  #if we remove username and add email we need to make custom Usermanager

    
    
    def __str__(self):
        return self.username
    


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    bio = models.TextField(blank=True, null=True)

    phone_number = PhoneNumberField(blank=True)

    profile_image = models.ImageField(
        upload_to="profile_images/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
class Workplace(models.Model):
    name = models.CharField()
    description = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owner_workplace"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}"
    
