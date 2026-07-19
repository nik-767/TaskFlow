from .models import Profile ,CustomUser , Workspace , WorkspaceMembers , Project , Board ,Task , Flow
from rest_framework import serializers 

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email' , 'password', 'confirm_password']  # Sirf yahi fields frontend ko JSON me dikhenge
        extra_kwargs = {
            'password' : {'write_only' : True}
        }

    def validate(self, attrs): #attrs (Data Ka Dabba): attrs ek simple Python Dictionary hai jisme user ka bheja hua
        # saara data hota hai (jaise: {"username": "bhai", "password": "123", "confirm_password": "456"}).
        # Using .get() prevents KeyError crashes if fields are missing from the request
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )
        return attrs
        
        
    
    def create(self, validated_data):
        # Safely remove confirm_password from data dictionary
        validated_data.pop('confirm_password', None)
        
        # Cleaner approach: pass dictionary directly using keyword unpacking (**)
        return CustomUser.objects.create_user(**validated_data)

    

    
class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = "__all__"

class WorkplaceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Workspace
        fields = '__all__'
        read_only_fields = ['owner'] #only can read
        
class WorkSpaceMemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkspaceMembers
        fields = '__all__'
        read_only_fields = [ 'joined_at']

    def validate(self, validate_data):
            # incoming data se workspace or role nikalna
            workspace = validate_data.get('workspace')
            role = validate_data.get('role') # means owner

            if role == 'owner':
            #check karo owner ha ya nhi workplace ma
                exist_owner = WorkspaceMembers.objects.filter(
                    workspace = workspace,
                    role = 'owner'
            )
    # self.instance check karta hai ki ye UPDATE (PUT/PATCH) hai ya CREATE (POST)
                if self.instance:
                    exist_owner = exist_owner.exclude(pk=self.instance.pk)

     # 4. Agar koi doosra owner mil jata hai, toh error raise karo
                if exist_owner.exists():
                    raise serializers.ValidationError({
                "role": "This workspace already has an owner. Only one owner is allowed."
                })
        
            return validate_data

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['created_by']

class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['reporter']

class Flowserializer(serializers.ModelSerializer):

    class Meta:
        model = Flow
        fields = '__all__'