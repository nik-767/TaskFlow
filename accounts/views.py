from django.shortcuts import render
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework_simplejwt.tokens import RefreshToken  # Tool used to manually generate tokens
from .serializers import RegisterSerializer , ProfileSerializer
from .models import Profile ,CustomUser
from rest_framework.views import APIView 
from rest_framework.permissions import IsAuthenticated

# Create your views here.

def GenToken(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access' :str(refresh.access_token),
    }

    
class Register_api(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = GenToken(user)
            return Response (
            {
            "message" : "register successfully",
                "tokens" : token,
            }, status=status.HTTP_201_CREATED) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileAPi(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes =[IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)
