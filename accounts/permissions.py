# core/permissions.py

from rest_framework.permissions import BasePermission
from .models import WorkspaceMembers


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
    
        return WorkspaceMembers.objects.filter(
            workspace = obj.workspace,
            user=request.user,
            role__in=['owner', 'admin']
    ).exists()