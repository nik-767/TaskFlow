"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from accounts.views import Register_api , ProfileAPi , WorkplaceAPI , WorkspaceMemberView , Projectview , BoardView
from rest_framework.routers import DefaultRouter
from django.urls import path, include

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)
router = DefaultRouter()
router.register(r'profile', ProfileAPi , basename='profile')
router.register('workplace', WorkplaceAPI, basename='workplace')
router.register('projects', Projectview, basename='project')
router.register('members', WorkspaceMemberView, basename='workspace-member')
router.register('boards', BoardView, basename='board')

urlpatterns = [
    path('admin/', admin.site.urls),
    # Is URL par email/password POST karne se Access aur Refresh token milenge 
    # (Login endpoint)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # Is URL par Refresh Token bhejne se naya Access Token mil jata hai
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', Register_api.as_view()),
    path('', include(router.urls))
    

]
