from rest_framework import serializers
from .models import ComplaintsBook

class ComplaintsBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintsBook
        fields = '__all__'
    file_upload = serializers.FileField(required=False)
