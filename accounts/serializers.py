from .models import Profile ,CustomUser
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

    def validate(self, attrs):
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
