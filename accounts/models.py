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
    
class Workspace(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="owner_workplace",
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}"
    
class WorkspaceMembers(models.Model):
    RoleChoice =  [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('manager','Manager'),
        ('developer','Developer'),
        ('viewer','Viewer'),
    ]
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE,related_name='Members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    roles = models.CharField(max_length=20, choices=RoleChoice)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('workspace', 'user')

class Project(models.Model):
    workspace = models.ForeignKey(Workspace,on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    description = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL ,null=True, related_name='created_projects')
    created_at = models.DateTimeField(auto_now_add=True)

class Board(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Task(models.Model):
    STATUS_CHOICES = [('todo', 'Todo'), ('in_progress', 'In Progress'), ('review', 'Review'), ('done', 'Done')]
    PRIORITY_CHOICES = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')]
    title = models.CharField(max_length=200)
    description = models.TextField( blank=True)
    project = models.ForeignKey(Board, on_delete=models.CASCADE)
    assigned = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL , null=True , related_name='reported_tasks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    deadline = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title