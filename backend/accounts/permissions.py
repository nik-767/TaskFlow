# core/permissions.py
from rest_framework.permissions import BasePermission
from .models import Board, Project, WorkspaceMembers ,Task , Flow


class IsWorkspaceAdminOrOwner(BasePermission):
    """
    Allows access only to users who are 'owner' or 'admin' 
    in the specific workspace being acted on.
    """

    def has_permission(self, request, view):
        if request.method in ( 'GET', 'HEAD','OPTIONS'):
            return True #sirf dekhna h toh sbb allow kr doh .
        
        workspace_id = view.kwargs.get('workspace_pk') or request.data.get('workspace')

        if not workspace_id:
            return False
        
        return WorkspaceMembers.objects.filter(
            workspace_id=workspace_id,
            user=request.user,
            role__in = ['owner', 'admin']
        ).exists()
    
    def has_object_permission(self, request , view , obj):

        if request.method in ('GET' , 'HEAD', 'OPTIONS'):
            return True
        
        workspace = obj.workspace if hasattr(obj, 'workspace') else obj.project.workspace

        return WorkspaceMembers.objects.filter(
            workspace = workspace,
            user=request.user,
            role__in=['owner', 'admin']
    ).exists()

class IsTaskAssigneeOrWorkspaceAdmin(BasePermission):

    def has_permission(self, request, view):

        if request.method in ( 'GET', 'HEAD','OPTIONS'):
            return True
        
        project_id = request.data.get('project')
        if not project_id:
            return False

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return False
        
        return WorkspaceMembers.objects.filter(
            workspace=project.workspace,
            user=request.user,
        ).exists()

    
    def has_object_permission(self, request , view , obj):

        if request.method in ('GET' , 'HEAD', 'OPTIONS'):
            return True
        
        
        workspace = obj.project.workspace
     
        # Check A: Kya user is Task ka Assignee hai? (Aapke model mein field 'assigned' hai)
        if obj.assigned == request.user:
            return True

        return WorkspaceMembers.objects.filter(
            workspace = workspace,
            user=request.user,
            role__in=['owner', 'admin']
    ).exists()

class IsflowWork(BasePermission):

    def has_permission(self, request, view):
        if request.method in ('GET' , 'HEAD' , 'OPTIONS'):
            return request.user and request.user.is_authenticated
        
        task_id = view.kwargs.get('task_pk') or request.data.get('task')

        if not task_id:
            return False
        
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return False

        return WorkspaceMembers.objects.filter(
            workspace=task.project.workspace,
            user=request.user
        ).exists()
    def has_object_permission(self, request, view, obj):
        if request.method in ('GET', 'HEAD' , 'OPTIONS'):
            return True
        
        if obj.user == request.user:
            return True
        
        # Case 2: not the author, but check if they're Owner/Admin in this comment's workspace
        workspace = obj.task.project.workspace

        return WorkspaceMembers.objects.filter(
        workspace=workspace,
        user=request.user,
        role__in=['owner', 'admin']
    ).exists()