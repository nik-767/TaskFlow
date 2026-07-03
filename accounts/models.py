from django.contrib.auth.models import AbstractUser
from django.db import models
# Create your models here.
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'username'

    # 4. Fields required when running 'python manage.py createsuperuser'
    REQUIRED_FIELDS = ['email']  #if we remove username and add email we need to make custom Usermanager

    
    def __str__(self):
        return self.username