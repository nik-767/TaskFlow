from django.shortcuts import render
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework_simplejwt.tokens import RefreshToken  # Tool used to manually generate tokens
from .serializers import RegisterSerializer , ProfileSerializer , WorkplaceSerializer , WorkSpaceMemberSerializer , ProjectSerializer , BoardSerializer , TaskSerializer , Flowserializer
from .models import Profile ,CustomUser ,Workspace, WorkspaceMembers , Project , Board , Task , Flow
from rest_framework.views import APIView 
from rest_framework.permissions import IsAuthenticated 
from .permissions import IsWorkspaceAdminOrOwner , IsflowWork

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

class WorkplaceAPI(viewsets.ModelViewSet):
    serializer_class = WorkplaceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Workspace.objects.filter(owner=self.request.user) # only thr requested user profile visible not all .
      
    def perform_create(self ,serializer):
        serializer.save(owner=self.request.user)

class WorkspaceMemberView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsWorkspaceAdminOrOwner]
    serializer_class = WorkSpaceMemberSerializer
    
    #Yahan workspace__members__user ka matlab: "us WorkspaceMembers row ke workspace field se hoke,
    #  uske members (related_name) se hoke, unme se user field match karo current user se."
    # Ye asli double-underscore lookup hai — query ke andar, request.user ke peeche nahi.
    def get_queryset(self):
        return WorkspaceMembers.objects.filter(workspace__Members__user=self.request.user)
    
    def perform_create(self,serailizer):
        serailizer.save()

class Projectview(viewsets.ModelViewSet):
    permission_classes = [IsWorkspaceAdminOrOwner]
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.filter(Workspace__Members__user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class BoardView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated , IsWorkspaceAdminOrOwner]
    serializer_class = BoardSerializer

    def get_queryset(self):
        return Board.objects.filter(Project__workspace__Members__user=self.request.user)

class TaskView(viewsets.ModelViewSet):
    Permission_classes = [IsAuthenticated , IsWorkspaceAdminOrOwner]
    serializer_class = TaskSerializer

    def get_queryset(self):
            return Task.objects.filter(project__workspace__Members__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)
    
class FlowView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated,IsflowWork]
    serializer_class = Flowserializer

    def get_queryset(self):
        return Flow.objects.filter(task__project__workspace__Members__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)