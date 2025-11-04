from rest_framework import serializers

class GoogleAuthSerializer(serializers.Serializer):
    """
    Serializer for Google OAuth authentication data
    """
    code = serializers.CharField(required=False)
    error = serializers.CharField(required=False)
    
    def validate(self, data):
        """
        Validate that either code or error is present, but not both
        """
        if 'code' not in data and 'error' not in data:
            raise serializers.ValidationError("Either 'code' or 'error' must be provided")
        if 'code' in data and 'error' in data:
            raise serializers.ValidationError("Only one of 'code' or 'error' should be provided")
        return data

class GoogleUserInfoSerializer(serializers.Serializer):
    """
    Serializer for Google user information
    """
    email = serializers.EmailField()
    verified_email = serializers.BooleanField()
    name = serializers.CharField()
    given_name = serializers.CharField(required=False)
    family_name = serializers.CharField(required=False)
    picture = serializers.URLField(required=False)
    locale = serializers.CharField(required=False)
