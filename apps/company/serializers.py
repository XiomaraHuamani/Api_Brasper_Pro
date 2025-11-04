from rest_framework import serializers
from .models import PopupImage

class PopupImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PopupImage
        fields = ['id', 'image_pe','image_br', 'date', 'country', 'alias', 'start_date','end_date','is_active','created_at']
