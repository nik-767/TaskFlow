from .models import Profile ,CustomUser
from rest_framework import serializers 

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email' , 'password']  # Sirf yahi fields frontend ko JSON me dikhenge
        extra_kwargs = {
            'password' : {'write_only' : True}
        }
    
    def create(self, validated_data):
        """
    Overriding the default create method of ModelSerializer.
    
    Why this works: 
    Django's built-in manager function 'create_user()' has internal logic that 
    automatically extracts the 'password' argument, passes it through set_password() 
    cryptographic hashing, and inserts the row cleanly into the database.
    """
        return CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
    
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"
